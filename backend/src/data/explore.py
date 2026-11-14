from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Assumes bands span 450-950 nm in 4 nm steps: index = (wavelength - 450) / 4
RED_BAND, GREEN_BAND, BLUE_BAND = 50, 25, 5


def summarize_cube(cube: np.ndarray) -> dict:
    return {
        "shape": cube.shape,
        "min": float(cube.min()),
        "max": float(cube.max()),
        "mean": float(cube.mean()),
        "nan_count": int(np.isnan(cube).sum()),
    }


def false_color(cube: np.ndarray) -> np.ndarray:
    """Build a rough RGB preview (height, width, 3) scaled to [0, 1]."""
    bands = min(cube.shape[0] - 1, max(RED_BAND, GREEN_BAND, BLUE_BAND))
    idx = [min(RED_BAND, bands), min(GREEN_BAND, bands), min(BLUE_BAND, bands)]
    rgb = np.stack([cube[i] for i in idx], axis=-1)
    lo, hi = np.percentile(rgb, [2, 98])
    return np.clip((rgb - lo) / (hi - lo + 1e-8), 0, 1)


def save_preview(cube: np.ndarray, out_path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].imshow(false_color(cube))
    axes[0].set_title("False-color preview")
    axes[0].axis("off")
    axes[1].plot(cube.mean(axis=(1, 2)))
    axes[1].set_title("Mean spectrum")
    axes[1].set_xlabel("Band index")
    axes[1].set_ylabel("Reflectance")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
