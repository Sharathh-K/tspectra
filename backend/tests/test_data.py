import numpy as np
import pytest

from src.data.loader import get_cube_shape, read_cube
from src.data.preprocess import band_stats, minmax_per_band


def test_read_cube_shape(tmp_path):
    f = tmp_path / "cube.npy"
    np.save(f, np.random.rand(125, 20, 20))
    assert get_cube_shape(f) == (125, 20, 20)


def test_read_cube_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_cube(tmp_path / "nope.npy")


def test_minmax_range():
    cube = np.random.rand(10, 8, 8).astype(np.float32) * 500
    out = minmax_per_band(cube)
    assert out.min() >= 0.0
    assert out.max() <= 1.0 + 1e-6


def test_band_stats_shape():
    mean, std = band_stats(np.random.rand(10, 8, 8))
    assert mean.shape == (10,)
    assert std.shape == (10,)
