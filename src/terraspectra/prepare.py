"""Week 1: inspect TIFFs, split labelled images, and compress spectral bands."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import joblib
import numpy as np
import rasterio
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
CLASSES = {"Health": 0, "Other": 1, "Rust": 2}


def extract_dataset(archive, destination):
    """Extract only dataset TIFFs; keep the original train/val folders."""
    destination = Path(destination)
    with ZipFile(archive) as source:
        for member in source.infolist():
            name = Path(member.filename)
            if member.is_dir():
                continue
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("Unsafe archive path: " + member.filename)
            if name.suffix.lower() not in {".tif", ".tiff"}:
                continue
            target = destination / name
            if not target.exists() or target.stat().st_size != member.file_size:
                source.extract(member, destination)


def read_cube(path):
    """Rasterio returns bands first. Our arrays use height, width, bands."""
    with rasterio.open(path) as image:
        masked = image.read(masked=True).astype(np.float32)
        cube = np.moveaxis(masked.filled(np.nan), 0, -1)
    # Some TIFFs append a binary 0/65535 plane after the 125 spectral bands.
    # Its undocumented meaning is not used as a disease label or missing-data mask.
    if cube.shape[-1] == 126:
        if not np.isin(cube[:, :, -1], [0, 65535]).all():
            raise ValueError(f"Unexpected extra band in {path}; inspect it manually.")
        cube = cube[:, :, :125]
    if cube.ndim != 3 or not np.isfinite(cube).all():
        raise ValueError(f"Invalid or missing pixel values in {path}")
    return cube


def build_inventory(raw):
    rows = []
    for path in sorted(raw.rglob("*.tif")):
        relative = path.relative_to(raw)
        labelled = relative.parts[0] == "train" and relative.parts[1] in CLASSES
        with rasterio.open(path) as image:
            if image.count not in {125, 126}:
                raise ValueError(f"Unexpected band count in {path}: {image.count}")
            if image.count == 126 and not np.isin(image.read(126), [0, 65535]).all():
                raise ValueError(f"Extra band is not binary 0/65535: {path}")
            rows.append({
                "path": relative.as_posix(),
                "label": relative.parts[1] if labelled else "unlabelled",
                "class_id": CLASSES[relative.parts[1]] if labelled else -1,
                "split": "pending" if labelled else "unlabelled",
                "height": image.height, "width": image.width, "bands": 125,
                "raw_bands": image.count, "dropped_extra_band": image.count == 126,
                "dtype": image.dtypes[0], "crs": str(image.crs),
                "transform": str(tuple(image.transform)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
    if not rows:
        raise ValueError("No TIFF images found. Check --zip or --raw.")
    if len({(r['height'], r['width'], r['bands']) for r in rows}) != 1:
        raise ValueError("Images have different shapes; inspect before stacking.")
    return rows


def prepare(archive=None, raw=ROOT / "data/raw", components=16, pixels_per_image=64,
            seed=42):
    raw = Path(raw)
    output = ROOT / "data/processed"
    reports = ROOT / "reports"
    output.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    if archive:
        extract_dataset(archive, raw)
    rows = build_inventory(raw)
    labelled = [i for i, row in enumerate(rows) if row["class_id"] >= 0]
    train, validation = train_test_split(
        labelled, test_size=0.2, random_state=seed,
        stratify=[rows[i]["class_id"] for i in labelled],
    )
    for indices, split in [(train, "train"), (validation, "validation")]:
        for index in indices:
            rows[index]["split"] = split
    # Exact copies in two partitions would make evaluation misleading.
    hashes = {}
    for row in rows:
        previous = hashes.setdefault(row["sha256"], row["split"])
        if previous != row["split"]:
            raise ValueError("Identical files cross partitions. Group duplicates first.")
    bands = rows[0]["bands"]
    if not 1 <= components <= bands:
        raise ValueError(f"Components must be between 1 and {bands}.")
    rng = np.random.default_rng(seed)
    samples = []
    for index in train:
        pixels = read_cube(raw / rows[index]["path"]).reshape(-1, bands)
        chosen = rng.choice(len(pixels), min(pixels_per_image, len(pixels)), replace=False)
        samples.append(pixels[chosen])
    # Only this small TRAINING pixel sample teaches the scaler and PCA.
    sample = np.concatenate(samples)
    scaler = StandardScaler().fit(sample)
    pca = PCA(n_components=components, svd_solver="randomized", random_state=seed)
    pca.fit(scaler.transform(sample))
    joblib.dump({"scaler": scaler, "pca": pca, "class_names": CLASSES,
                 "seed": seed, "bands": bands}, reports / "preprocessing.joblib")
    for number, row in enumerate(rows, start=1):
        cube = read_cube(raw / row["path"])
        pixels = cube.reshape(-1, bands)
        reduced = pca.transform(scaler.transform(pixels))
        reduced = reduced.reshape(cube.shape[0], cube.shape[1], components).astype("float32")
        destination = Path(row["split"]) / Path(row["path"]).relative_to(Path(row["path"]).parts[0])
        destination = destination.with_suffix(".npy")
        (output / destination).parent.mkdir(parents=True, exist_ok=True)
        np.save(output / destination, reduced)
        row["processed_path"] = destination.as_posix()
        if number % 150 == 0:
            print(f"Prepared {number}/{len(rows)} images", flush=True)
    with (reports / "inventory.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "source": "Kaggle Beyond Visible Spectrum: AI for Agriculture 2023",
        "files": len(rows), "shape_hwb": [rows[0]["height"], rows[0]["width"], bands],
        "raw_band_counts": dict(Counter(r["raw_bands"] for r in rows)),
        "binary_extra_bands_removed": sum(r["dropped_extra_band"] for r in rows),
        "classes": dict(Counter(r["label"] for r in rows)),
        "splits": dict(Counter(r["split"] for r in rows)), "class_ids": CLASSES,
        "pca_components": components, "training_pixels_sampled": len(sample),
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "retained_variance": float(pca.explained_variance_ratio_.sum()), "seed": seed,
        "geography": "Unverified CRS/transform; do not locate these patches on the demo farm.",
        "evaluation_limit": "Patch split only: farm/date grouping unavailable; not a field-generalization score.",
    }
    (reports / "dataset_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    # The dashboard displays real inventory counts, never invented disease scores.
    public = ROOT / "frontend/public"
    public.mkdir(parents=True, exist_ok=True)
    (public / "dataset-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, help="Path to the downloaded Kaggle ZIP")
    parser.add_argument("--raw", type=Path, default=ROOT / "data/raw")
    parser.add_argument("--components", type=int, default=16)
    args = parser.parse_args()
    prepare(args.zip, args.raw, args.components)
