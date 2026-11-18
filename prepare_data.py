import glob
import os
import numpy as np
import rasterio
from sklearn.decomposition import PCA

DATA_DIR = "data/train"
CLASSES = ["Health", "Other", "Rust"]
N_COMPONENTS = 10
OUT_FILE = "data/processed_train.npz"
PIXELS_PER_PATCH = 500


def load_patch(path):
    with rasterio.open(path) as src:
        a = src.read().astype("float32")
    return a / 10000.0  # raw values go up to ~5000, so this scales them to ~0-0.5


files, labels = [], []
for idx, cls in enumerate(CLASSES):
    found = sorted(glob.glob(os.path.join(DATA_DIR, cls, "*.tif")))
    files += found
    labels += [idx] * len(found)
print("total patches:", len(files))

# Pass 1: sample some pixels from every patch and fit PCA on them
rng = np.random.default_rng(42)
samples = []
for f in files:
    a = load_patch(f)
    pix = a.reshape(a.shape[0], -1).T  # (4096 pixels, 125 bands)
    pick = rng.choice(pix.shape[0], PIXELS_PER_PATCH, replace=False)
    samples.append(pix[pick])
samples = np.concatenate(samples)
pca = PCA(n_components=N_COMPONENTS).fit(samples)
print("variance kept:", round(float(pca.explained_variance_ratio_.sum()), 4))

# Pass 2: shrink every patch from 125 bands to N_COMPONENTS
X = np.zeros((len(files), N_COMPONENTS, 64, 64), dtype="float32")
for i, f in enumerate(files):
    a = load_patch(f)
    pix = a.reshape(a.shape[0], -1).T
    X[i] = pca.transform(pix).T.reshape(N_COMPONENTS, 64, 64)

np.savez_compressed(
    OUT_FILE,
    X=X,
    y=np.array(labels),
    classes=np.array(CLASSES),
    pca_mean=pca.mean_,
    pca_components=pca.components_,
)
print("saved", OUT_FILE, "X shape:", X.shape)
