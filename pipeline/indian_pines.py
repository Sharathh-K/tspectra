"""Download and load the Indian Pines hyperspectral scene (AVIRIS, 145 x 145 pixels, 200 bands).

Source (CC0 mirror): https://huggingface.co/datasets/danaroth/indian_pines
Original data: Baumgardner, Biehl, Landgrebe (2015), Purdue University Research Repository,
doi:10.4231/R7RX991C. Collected/distributed by Grana, Veganzones, Ayerdi (UPV/EHU).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io as sio

REPO_ID = "danaroth/indian_pines"
DEFAULT_DIR = Path("data/indian_pines")

# "Corrected" version: the 20 water-absorption bands are already removed, leaving 200 bands.
FILES = {"cube": "Indian_pines_corrected.mat", "gt": "Indian_pines_gt.mat"}
MAT_KEYS = {"cube": "indian_pines_corrected", "gt": "indian_pines_gt"}
EXPECTED_SHAPE = (145, 145, 200)

CLASS_NAMES = {
    0: "Unlabeled",
    1: "Alfalfa",
    2: "Corn-notill",
    3: "Corn-mintill",
    4: "Corn",
    5: "Grass-pasture",
    6: "Grass-trees",
    7: "Grass-pasture-mowed",
    8: "Hay-windrowed",
    9: "Oats",
    10: "Soybean-notill",
    11: "Soybean-mintill",
    12: "Soybean-clean",
    13: "Wheat",
    14: "Woods",
    15: "Buildings-Grass-Trees-Drives",
    16: "Stone-Steel-Towers",
}

# Published per-class pixel counts, used as a sanity check on the downloaded files.
EXPECTED_COUNTS = {
    1: 46, 2: 1428, 3: 830, 4: 237, 5: 483, 6: 730, 7: 28, 8: 478,
    9: 20, 10: 972, 11: 2455, 12: 593, 13: 205, 14: 1265, 15: 386, 16: 93,
}


def download(data_dir: Path | str = DEFAULT_DIR) -> None:
    """Fetch the .mat files from Hugging Face into data_dir (skips files that already exist)."""
    data_dir = Path(data_dir)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as err:
        raise ImportError(
            "huggingface_hub is not installed. Run `pip install huggingface_hub`, or download "
            f"{list(FILES.values())} manually from https://huggingface.co/datasets/{REPO_ID} "
            f"into {data_dir}/"
        ) from err

    data_dir.mkdir(parents=True, exist_ok=True)
    for name in FILES.values():
        if not (data_dir / name).exists():
            hf_hub_download(
                repo_id=REPO_ID, filename=name, repo_type="dataset", local_dir=str(data_dir)
            )


def load(
    data_dir: Path | str = DEFAULT_DIR, download_if_missing: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """Return (cube, gt): cube is (H, W, bands), gt is (H, W) with 0 = unlabeled, 1..16 = class."""
    data_dir = Path(data_dir)
    missing = [name for name in FILES.values() if not (data_dir / name).exists()]
    if missing:
        if not download_if_missing:
            raise FileNotFoundError(f"Missing in {data_dir}: {missing}")
        download(data_dir)

    cube = sio.loadmat(str(data_dir / FILES["cube"]))[MAT_KEYS["cube"]]
    gt = sio.loadmat(str(data_dir / FILES["gt"]))[MAT_KEYS["gt"]]

    if cube.shape[:2] != gt.shape:
        raise ValueError(f"Cube {cube.shape} and ground truth {gt.shape} do not line up")
    if cube.shape != EXPECTED_SHAPE:
        print(f"Warning: expected cube shape {EXPECTED_SHAPE}, got {cube.shape}")
    return cube, gt
