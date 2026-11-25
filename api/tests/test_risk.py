import json
import unittest
from pathlib import Path

import httpx
import numpy as np
import rasterio
from rasterio.warp import transform

from api.main import app, SCENE

ROOT = Path(__file__).resolve().parents[2]


class RiskAPI(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_contract(self):
        fixture = json.loads((ROOT / "dashboard/public/mock/risk.json").read_bytes())
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            for path in ("/risk", "/risk?date=" + fixture["date"]):
                response = await client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), fixture)
            self.assertEqual((await client.get("/risk?date=2000-01-01")).status_code, 404)
            self.assertEqual((await client.get("/risk?date=invalid")).status_code, 422)


class RasterAlignment(unittest.TestCase):
    def test_vertices_centres_and_labels(self):
        scene = json.loads(SCENE.read_bytes())
        raster = ROOT / "data/mock/mock_labels.tif"
        if not raster.exists():
            self.skipTest("Run notebook 02 to regenerate the reference GeoTIFF.")
        with rasterio.open(raster) as src:
            h, w = src.shape
            self.assertEqual((scene["height"], scene["width"]), (h, w))
            np.testing.assert_array_equal(scene["labels"], src.read(1).ravel())
            corners = np.asarray(scene["corners"]).reshape(h+1, w+1, 2)
            rows, cols = np.indices((h+1, w+1))
            expected = src.transform * (cols.ravel(), rows.ravel())
            actual = transform("EPSG:4326", src.crs, *corners.reshape(-1, 2).T)
            np.testing.assert_allclose(actual, expected, atol=0.001, rtol=0)
            centres = (corners[:-1,:-1] + corners[:-1,1:] + corners[1:,1:] + corners[1:,:-1]) / 4
            rows, cols = np.indices((h, w))
            expected = src.transform * (cols.ravel()+0.5, rows.ravel()+0.5)
            actual = transform("EPSG:4326", src.crs, *centres.reshape(-1, 2).T)
            errors = np.hypot(np.subtract(actual[0],expected[0]),np.subtract(actual[1],expected[1]))
            self.assertLess(errors.max(), 0.001)
            print(f"All {h*w} centres align; maximum centre error {errors.max():.6f} m.")
