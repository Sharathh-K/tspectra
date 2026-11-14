import joblib
import numpy as np
from sklearn.decomposition import PCA


def cube_to_pixels(cube: np.ndarray) -> np.ndarray:
    """(bands, h, w) -> (h*w, bands)."""
    bands = cube.shape[0]
    return cube.reshape(bands, -1).T


def pixels_to_cube(pixels: np.ndarray, height: int, width: int) -> np.ndarray:
    """(h*w, k) -> (k, h, w)."""
    return pixels.T.reshape(-1, height, width)


def sample_pixels(cube: np.ndarray, n: int, seed: int = 42) -> np.ndarray:
    pixels = cube_to_pixels(cube)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pixels), size=min(n, len(pixels)), replace=False)
    return pixels[idx]


def fit_pca(samples: np.ndarray, n_components: int = 15, seed: int = 42) -> PCA:
    pca = PCA(n_components=n_components, random_state=seed)
    pca.fit(samples)
    return pca


def apply_pca(cube: np.ndarray, pca: PCA) -> np.ndarray:
    _, height, width = cube.shape
    reduced = pca.transform(cube_to_pixels(cube))
    return pixels_to_cube(reduced, height, width).astype(np.float32)


def save_pca(pca: PCA, path) -> None:
    joblib.dump(pca, path)


def load_pca(path) -> PCA:
    return joblib.load(path)
