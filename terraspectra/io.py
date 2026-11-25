"""Export the georeferenced mock scene built by notebooks 02 and 03."""
import base64
import io
import json
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.warp import transform

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "data/mock"
SCENE_DATE = "2026-11-13"  # Demo acquisition date associated with notebook 02.


def make_scene():
    with rasterio.open(MOCK / "mock_cube.tif") as src, rasterio.open(MOCK / "mock_labels.tif") as lab:
        if (src.shape, src.transform, src.crs) != (lab.shape, lab.transform, lab.crs):
            raise ValueError("Cube and label rasters must have identical georeferencing.")
        if src.crs.to_epsg() != 32643:
            raise ValueError("The mock field uses metre coordinates in UTM zone 43N.")
        height, width = src.shape
        affine = src.transform
        labels = lab.read(1)
        if not np.isin(labels, [0, 1]).all():
            raise ValueError("Expected binary mock stress labels.")
        # True pixel edges include the final row and column of vertices.
        rows, cols = np.indices((height + 1, width + 1))
        east, north = affine * (cols.ravel(), rows.ravel())
        lon, lat = transform(src.crs, "EPSG:4326", east, north)
        corners = np.column_stack((lon, lat)).round(9).tolist()

        waves = np.fromstring(src.tags()["wavelengths_nm"], sep=",")
        # Stretch the near-infrared, red and green bands independently for display.
        indices = [int(np.abs(waves - nm).argmin()) + 1 for nm in (550, 820, 670)]
        rgb = src.read(indices).transpose(1, 2, 0)
        lo, hi = np.percentile(rgb, [2, 98], axis=(0, 1))
        rgb = np.clip((rgb - lo) / np.maximum(hi - lo, 1e-8), 0, 1)
        image = io.BytesIO()
        Image.fromarray((rgb * 255).astype("uint8")).save(image, format="PNG")
        return {
            "date": SCENE_DATE, "field": "Mock farm", "source": "Synthetic stress labels",
            "crs": "EPSG:4326", "source_crs": src.crs.to_string(),
            "width": width, "height": height, "band_count": src.count,
            "pixel_area_m2": abs(affine.a * affine.e - affine.b * affine.d),
            "corners": corners, "labels": labels.ravel().tolist(),
            "image": "data:image/png;base64," + base64.b64encode(image.getvalue()).decode("ascii"),
        }


if __name__ == "__main__":
    payload = json.dumps(make_scene(), separators=(",", ":")) + "\n"
    for path in (MOCK / "mock_risk.json", ROOT / "dashboard/public/mock/risk.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        print(path.relative_to(ROOT))
