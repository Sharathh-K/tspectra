from pathlib import Path

import numpy as np

from src.config import RAW_DIR

VALID_EXTENSIONS = {".tif", ".tiff", ".npy"}


def list_cube_files(folder=RAW_DIR):
    """Return sorted list of cube files found under the folder."""
    folder = Path(folder)
    return sorted(p for p in folder.rglob("*") if p.suffix.lower() in VALID_EXTENSIONS)


def read_cube(path) -> np.ndarray:
    """Read a hyperspectral cube as float32 array shaped (bands, height, width)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Cube file not found: {path}")
    if path.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    if path.suffix.lower() == ".npy":
        cube = np.load(path)
    else:
        import rasterio

        with rasterio.open(path) as src:
            cube = src.read()
    return cube.astype(np.float32)


def get_cube_shape(path) -> tuple:
    return read_cube(path).shape
