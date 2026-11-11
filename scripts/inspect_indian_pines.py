"""Load and inspect the Indian Pines scene: print a data summary and save diagnostic figures.

Usage (from the repo root):
    python scripts/inspect_indian_pines.py
    python scripts/inspect_indian_pines.py --data-dir data/indian_pines --out-dir reports/figures --show
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `pipeline` imports from the repo root

import numpy as np  # noqa: E402

from pipeline.indian_pines import CLASS_NAMES, EXPECTED_COUNTS, load  # noqa: E402

RGB_BANDS = (43, 21, 11)  # approximate R, G, B bands for AVIRIS, used for a false-colour preview


def print_summary(cube: np.ndarray, gt: np.ndarray) -> None:
    print("=== Cube ===")
    print(f"shape (H, W, bands): {cube.shape}")
    print(f"dtype: {cube.dtype}   memory: {cube.nbytes / 1e6:.1f} MB")
    print(f"value range: min={cube.min()}  max={cube.max()}  mean={cube.mean():.1f}")
    bad = int((~np.isfinite(cube)).sum()) if np.issubdtype(cube.dtype, np.floating) else 0
    print(f"NaN/inf values: {bad}")
    print(f"all-zero pixels: {int((cube == 0).all(axis=2).sum())}")

    labelled = int((gt > 0).sum())
    print(f"\n=== Ground truth ===\nlabelled pixels: {labelled} of {gt.size} ({100 * labelled / gt.size:.1f}%)")
    print(f"{'id':>3}  {'class':<30}{'pixels':>7}{'%':>8}   check")
    counts = {int(k): int(v) for k, v in zip(*np.unique(gt, return_counts=True))}
    for cid in range(1, 17):
        n = counts.get(cid, 0)
        check = "ok" if n == EXPECTED_COUNTS[cid] else f"expected {EXPECTED_COUNTS[cid]}"
        print(f"{cid:>3}  {CLASS_NAMES[cid]:<30}{n:>7}{100 * n / labelled:>8.1f}   {check}")


def false_colour(cube: np.ndarray) -> np.ndarray:
    rgb = cube[:, :, list(RGB_BANDS)].astype(np.float64)
    lo, hi = np.percentile(rgb, (2, 98), axis=(0, 1))
    return np.clip((rgb - lo) / (hi - lo + 1e-9), 0, 1)


def class_cmap():
    from matplotlib.colors import ListedColormap
    import matplotlib.pyplot as plt

    colours = np.vstack([[0, 0, 0, 1], plt.get_cmap("tab20")(np.arange(16))])  # class 0 = black
    return ListedColormap(colours)


def save_overview(cube, gt, out_dir: Path) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    cmap = class_cmap()
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].imshow(false_colour(cube))
    axes[0].set_title(f"False-colour preview (bands {RGB_BANDS})")
    axes[1].imshow(gt, cmap=cmap, vmin=0, vmax=16, interpolation="nearest")
    axes[1].set_title("Ground truth")
    handles = [Patch(color=cmap(i / 16), label=f"{i} {CLASS_NAMES[i]}") for i in range(1, 17)]
    axes[1].legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7)
    for ax in axes:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_dir / "overview.png", dpi=150, bbox_inches="tight")


def save_band_grid(cube, out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    idx = np.linspace(0, cube.shape[2] - 1, 6, dtype=int)
    fig, axes = plt.subplots(2, 3, figsize=(10, 7))
    for ax, b in zip(axes.ravel(), idx):
        ax.imshow(cube[:, :, b], cmap="gray")
        ax.set_title(f"band {b}")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_dir / "bands.png", dpi=150)


def save_class_spectra(cube, gt, out_dir: Path) -> None:
    import matplotlib.pyplot as plt

    cmap = class_cmap()
    fig, ax = plt.subplots(figsize=(10, 5))
    for cid in range(1, 17):
        ax.plot(cube[gt == cid].mean(axis=0), color=cmap(cid / 16), label=f"{cid} {CLASS_NAMES[cid]}")
    ax.set_xlabel("band index")
    ax.set_ylabel("mean value")
    ax.set_title("Mean spectrum per class")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7)
    fig.tight_layout()
    fig.savefig(out_dir / "class_spectra.png", dpi=150, bbox_inches="tight")


def save_redundancy(cube, out_dir: Path) -> None:
    """Band correlation and cumulative variance: shows why PCA is worth doing."""
    import matplotlib.pyplot as plt

    x = cube.reshape(-1, cube.shape[2]).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.nan_to_num(np.corrcoef(x, rowvar=False))
    xc = x - x.mean(axis=0)
    eig = np.linalg.eigvalsh(xc.T @ xc / (len(xc) - 1))[::-1]
    cum = np.cumsum(eig / eig.sum())
    n99 = int(np.searchsorted(cum, 0.99) + 1)
    print(f"\nPCA preview: {n99} of {x.shape[1]} components explain 99% of the variance")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    im = axes[0].imshow(corr, cmap="viridis", vmin=-1, vmax=1)
    axes[0].set_title("Band-to-band correlation")
    axes[0].set_xlabel("band")
    axes[0].set_ylabel("band")
    fig.colorbar(im, ax=axes[0], fraction=0.046)
    axes[1].plot(np.arange(1, len(cum) + 1), cum)
    axes[1].axhline(0.99, color="red", linestyle="--", linewidth=1)
    axes[1].set_title(f"Cumulative explained variance (99% at {n99} components)")
    axes[1].set_xlabel("number of components")
    axes[1].set_ylabel("explained variance")
    fig.tight_layout()
    fig.savefig(out_dir / "redundancy.png", dpi=150)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", default="data/indian_pines")
    parser.add_argument("--out-dir", default="reports/figures")
    parser.add_argument("--show", action="store_true", help="open the figures in windows as well")
    args = parser.parse_args()

    if not args.show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cube, gt = load(args.data_dir)
    print_summary(cube, gt)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    save_overview(cube, gt, out_dir)
    save_band_grid(cube, out_dir)
    save_class_spectra(cube, gt, out_dir)
    save_redundancy(cube, out_dir)
    print(f"\nFigures saved to {out_dir}/")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
