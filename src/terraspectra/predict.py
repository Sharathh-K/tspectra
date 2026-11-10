"""Predict one real TIFF patch using the exported Week 2 weights and PCA recipe."""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

from terraspectra.data import ROOT, make_input
from terraspectra.model import load_model
from terraspectra.prepare import read_cube


def preprocess_tiff(path, preprocessing=ROOT / "models/week2/preprocessing.npz"):
    cube = read_cube(path)
    if cube.shape != (64, 64, 125):
        raise ValueError("This Week 2 model accepts 64×64×125 spectral patches only.")
    with np.load(preprocessing, allow_pickle=False) as recipe:
        # Match StandardScaler's float32 operations before PCA projection.
        pixels = cube.reshape(-1, 125).copy()
        pixels -= recipe["scaler_mean"]
        pixels /= recipe["scaler_scale"]
        reduced = pixels @ recipe["pca_components"].T
        reduced -= recipe["pca_mean"] @ recipe["pca_components"].T
    return reduced.reshape(64, 64, 16).astype("float32")


def predict(path, model_dir=ROOT / "models/week2"):
    torch.set_num_threads(2)
    model_dir = Path(model_dir)
    model, checkpoint = load_model(model_dir / "hybrid_cnn.pt")
    cube = preprocess_tiff(path, model_dir / "preprocessing.npz")
    with torch.inference_mode():
        scores = model(make_input(cube).unsqueeze(0)).softmax(1)[0].numpy()
    names = checkpoint["class_names"]
    return {"file": Path(path).name, "predicted_class": names[int(scores.argmax())],
            "scores": dict(zip(names, map(float, scores))),
            "note": "Uncalibrated patch-class scores; no pixel mask or farm coordinates."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(predict(args.image), indent=2))
