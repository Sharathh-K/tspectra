"""Create a tiny synthetic 224-band GeoTIFF for the plan's mock-cube exercise."""
from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin


def make_mock_cube():
    root = Path(__file__).resolve().parents[2]
    path = root / "data/raw_mock/synthetic_224_band.tif"
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    cube = rng.random((224, 32, 32), dtype=np.float32)
    # This coordinate system belongs ONLY to the invented exercise.
    with rasterio.open(path, "w", driver="GTiff", height=32, width=32,
                       count=224, dtype="float32", crs="EPSG:4326",
                       transform=from_origin(77.591, 13.158, 0.0001, 0.0001)) as target:
        target.write(cube)
        target.update_tags(SOURCE="SYNTHETIC random numbers; never train disease models on this")
    print(path)
    return path


if __name__ == "__main__":
    make_mock_cube()
