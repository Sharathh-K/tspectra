import numpy as np


def minmax_per_band(cube: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Scale each band to [0, 1]. Cube shape: (bands, height, width)."""
    mins = cube.min(axis=(1, 2), keepdims=True)
    maxs = cube.max(axis=(1, 2), keepdims=True)
    return (cube - mins) / (maxs - mins + eps)


def band_stats(cube: np.ndarray):
    """Return per-band mean and std, each shaped (bands,)."""
    return cube.mean(axis=(1, 2)), cube.std(axis=(1, 2))
