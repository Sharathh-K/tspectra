"""Train once with a fixed small budget, compare a baseline, and save real results."""
import argparse
import csv
import hashlib
import json
import platform
import random
import resource
import time
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader

from terraspectra.data import ROOT, CLASS_NAMES, PatchDataset
from terraspectra.model import HybridCNN, HybridViT, load_model


def evaluate_scores(labels, probabilities):
    predicted = probabilities.argmax(axis=1)
    return {
        "accuracy": float(accuracy_score(labels, predicted)),
        "macro_f1": float(f1_score(labels, predicted, labels=[0, 1, 2], average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predicted, labels=[0, 1, 2]).tolist(),
        "per_class": classification_report(labels, predicted, labels=[0, 1, 2],
                                           target_names=CLASS_NAMES, output_dict=True, zero_division=0),
    }


def predict_loader(model, loader, device):
    model.eval()
    results = []
    with torch.inference_mode():
        for inputs, _ in loader:
            results.append(model(inputs.to(device)).softmax(dim=1).cpu().numpy())
    return np.concatenate(results)


def baseline_features(inputs):
    """Summarize each PCA page by its mean and spread: 16 × 2 = 32 numbers."""
    return np.concatenate([inputs.numpy().mean(axis=(3, 4)),
                           inputs.numpy().std(axis=(3, 4))], axis=2).reshape(len(inputs), 32)


def train(epochs=20, batch_size=16, patience=5, seed=42, device_name="cpu", root=ROOT, architecture="hybrid_cnn"):
    if architecture not in ("hybrid_cnn", "hybrid_vit"):
        raise ValueError("Unknown architecture")
    week = "week3" if architecture == "hybrid_vit" else "week2"
    model_name = "Compact CNN + vision transformer" if week == "week3" else "Compact hybrid 3D–2D CNN"
    if min(epochs, batch_size, patience) < 1:
        raise ValueError("Epochs, batch size and patience must be positive.")
    root = Path(root)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(2)  # Keep a laptop responsive; no multiprocessing workers.
    torch.use_deterministic_algorithms(True)
    if device_name == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA is unavailable. Use --device cpu.")
    device = torch.device(device_name)
    started = time.perf_counter()
    reports = root / "reports" / week
    models = root / "models" / week
    reports.mkdir(parents=True, exist_ok=True)
    models.mkdir(parents=True, exist_ok=True)
    training = PatchDataset("train", root)
    validation = PatchDataset("validation", root)
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(training, batch_size=batch_size, shuffle=True, generator=generator)
    val_loader = DataLoader(validation, batch_size=batch_size, shuffle=False)

    baseline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed))
    baseline.fit(baseline_features(training.inputs), training.labels.numpy())
    baseline_metrics = evaluate_scores(validation.labels.numpy(), baseline.predict_proba(baseline_features(validation.inputs)))

    model = (HybridViT() if week == "week3" else HybridCNN()).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0001)
    criterion = nn.CrossEntropyLoss()
    history, best_loss, best_epoch, stale = [], float("inf"), 0, 0
    for epoch in range(1, epochs + 1):
        epoch_start = time.perf_counter()
        model.train()
        total_loss, correct = 0.0, 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss = criterion(logits, labels)
            if not torch.isfinite(loss):
                raise ValueError("Non-finite training loss. Inspect the input arrays.")
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(labels)
            correct += int((logits.argmax(1) == labels).sum().item())
        probabilities = predict_loader(model, val_loader, device)
        labels = validation.labels.numpy()
        val_loss = float(-np.log(np.clip(probabilities[np.arange(len(labels)), labels], 1e-12, 1)).mean())
        scores = evaluate_scores(labels, probabilities)
        history.append({"epoch": epoch, "train_loss": total_loss / len(training),
                        "train_accuracy": correct / len(training), "val_loss": val_loss,
                        "val_accuracy": scores["accuracy"], "val_macro_f1": scores["macro_f1"],
                        "seconds": time.perf_counter() - epoch_start})
        print(f"Epoch {epoch:02d}: train loss {history[-1]['train_loss']:.3f}, "
              f"validation loss {val_loss:.3f}, macro F1 {scores['macro_f1']:.3f}", flush=True)
        if val_loss < best_loss - 0.0001:
            best_loss, best_epoch, stale = val_loss, epoch, 0
            torch.save({"state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
                        "architecture": architecture, "class_names": CLASS_NAMES, "best_epoch": epoch,
                        "input_shape": [1, 16, 16, 16], "seed": seed}, models / f"{architecture}.pt")
        else:
            stale += 1
            if stale >= patience:
                print("Early stopping: validation loss stopped improving.", flush=True)
                break

    # Evaluate the saved best checkpoint, not whichever weights happened to finish last.
    best_model, _ = load_model(models / f"{architecture}.pt")
    best_model.to(device)
    val_probabilities = predict_loader(best_model, val_loader, device)
    metrics = evaluate_scores(validation.labels.numpy(), val_probabilities)
    inference = PatchDataset("unlabelled", root)
    unlabelled_probs = predict_loader(best_model, DataLoader(inference, batch_size=batch_size), device)
    for dataset, probs, name in [(validation, val_probabilities, "validation_predictions.csv"),
                                 (inference, unlabelled_probs, "unlabelled_predictions.csv")]:
        with (reports / name).open("w", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["path", "true_label", "predicted_label", "p_Health", "p_Other", "p_Rust"])
            for row, prob in zip(dataset.rows, probs):
                writer.writerow([row["path"], row["label"], CLASS_NAMES[int(prob.argmax())], *prob.tolist()])

    # Export numeric preprocessing parameters, avoiding a pickle dependency at inference.
    recipe = joblib.load(root / "reports/preprocessing.joblib")
    if recipe["pca"].n_components_ != 16:
        raise ValueError("Week 2 expects the Week 1 16-component preprocessing recipe.")
    np.savez_compressed(models / "preprocessing.npz", scaler_mean=recipe["scaler"].mean_,
                        scaler_scale=recipe["scaler"].scale_, pca_mean=recipe["pca"].mean_,
                        pca_components=recipe["pca"].components_)
    elapsed = time.perf_counter() - started
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mib = peak / (1024 ** 2 if platform.system() == "Darwin" else 1024)
    report = {"model": model_name, "architecture": architecture, "classes": CLASS_NAMES,
              "parameters": sum(p.numel() for p in model.parameters()),
              "training_images": len(training), "validation_images": len(validation),
              "unlabelled_images": len(inference), "seed": seed, "device": str(device),
              "torch_version": str(torch.__version__), "python_version": platform.python_version(),
              "batch_size": batch_size, "max_epochs": epochs, "epochs_run": len(history),
              "best_epoch": best_epoch, "selection_rule": "minimum validation cross-entropy; patience 5 by default",
              "patience": patience, "learning_rate": 0.001, "weight_decay": 0.0001,
              "elapsed_seconds": elapsed, "peak_process_memory_mib": peak_mib,
              "input_batch_mib": batch_size * 16 * 16 * 16 * 4 / 1024 ** 2,
              "cached_labelled_inputs_mib": (training.inputs.numel() + validation.inputs.numel()) * 4 / 1024 ** 2,
              ("transformer" if week == "week3" else "cnn"): metrics, "baseline": baseline_metrics, "majority_baseline_accuracy": 1/3,
              "manifest_sha256": hashlib.sha256((root / "reports/inventory.csv").read_bytes()).hexdigest(),
              "preprocessing_sha256": hashlib.sha256((models / "preprocessing.npz").read_bytes()).hexdigest(),
              "checkpoint_sha256": hashlib.sha256((models / f"{architecture}.pt").read_bytes()).hexdigest(),
              "limitations": ["Patch labels, not pixel segmentation or chemical stress labels.",
                              "Development validation also selects the checkpoint; not an independent test.",
                              "Neighbouring source patches may share scenes; no verified farm/date grouping.",
                              "Softmax scores are uncalibrated. No three-week forecast or real farm heatmap."]}
    (reports / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    with (reports / "history.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(history)
    public = root / "frontend/public"
    (public / ("week3-summary.json" if week == "week3" else "model-summary.json")).write_text(json.dumps(report, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot([h["epoch"] for h in history], [h["train_loss"] for h in history], label="Train")
    axes[0].plot([h["epoch"] for h in history], [h["val_loss"] for h in history], label="Validation")
    axes[0].axvline(best_epoch, color="gray", linestyle="--", label="Saved epoch")
    axes[0].set(xlabel="Epoch", ylabel="Cross-entropy loss", title="Training history")
    axes[0].legend()
    matrix = np.asarray(metrics["confusion_matrix"])
    axes[1].imshow(matrix, cmap="Blues")
    axes[1].set(xticks=range(3), yticks=range(3), xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
                xlabel="Predicted class", ylabel="Actual class", title="Development validation (120 images)")
    for i in range(3):
        for j in range(3):
            axes[1].text(j, i, str(matrix[i, j]), ha="center", va="center",
                         color="white" if matrix[i, j] > matrix.max()/2 else "black")
    fig.tight_layout()
    fig.savefig(reports / "training_results.png", dpi=150)
    plt.close(fig)
    print(f"Finished in {elapsed:.1f}s. Model accuracy {metrics['accuracy']:.3f}; "
          f"baseline accuracy {baseline_metrics['accuracy']:.3f}. Saved epoch {best_epoch}.", flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--architecture", choices=["hybrid_cnn", "hybrid_vit"], default="hybrid_cnn")
    args = parser.parse_args()
    train(args.epochs, args.batch_size, args.patience, device_name=args.device, architecture=args.architecture)
