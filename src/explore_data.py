import glob
import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt

DATA_DIR = "data/train"
CLASSES = ["Health", "Other", "Rust"]

plt.figure(figsize=(8, 5))
for cls in CLASSES:
    files = sorted(glob.glob(os.path.join(DATA_DIR, cls, "*.tif")))[:20]
    spectra = []
    for f in files:
        with rasterio.open(f) as src:
            a = src.read().astype("float32")
        spectra.append(a.mean(axis=(1, 2)))
    mean_spec = np.mean(spectra, axis=0)
    print(cls, "patches used:", len(files), "avg value:", round(float(mean_spec.mean()), 1))
    plt.plot(mean_spec, label=cls)

plt.xlabel("Band number (1-125)")
plt.ylabel("Average pixel value")
plt.title("Average spectrum per class")
plt.legend()
plt.savefig("spectra_by_class.png", dpi=150)
print("saved spectra_by_class.png")
