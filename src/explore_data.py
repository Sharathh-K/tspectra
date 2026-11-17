from pathlib import Path
import numpy as np
import rasterio
import matplotlib.pyplot as plt

DATA = Path(r"E:\TerraSpectra\data\train")
CLASSES = ["Health", "Other", "Rust"]


def load(path):
    with rasterio.open(path) as src:
        return src.read().astype("float32")  # shape (125, 64, 64)


plt.figure(figsize=(8, 5))
for c in CLASSES:
    files = sorted((DATA / c).glob("*.tif"))[:20]
    mean_spectrum = np.mean([load(f).mean(axis=(1, 2)) for f in files], axis=0)
    plt.plot(mean_spectrum, label=c)

plt.xlabel("Band number (0-124)")
plt.ylabel("Average pixel value")
plt.title("Average spectrum per class (20 images each)")
plt.legend()
plt.savefig("spectra_by_class.png", dpi=120)
plt.show()
