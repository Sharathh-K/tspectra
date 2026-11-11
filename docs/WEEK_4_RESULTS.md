# Week 4 delivery record

## Completed

- FastAPI service reuses the saved Week 3 transformer and numeric preprocessing recipe.
- `GET /api/health`, binary TIFF `POST /api/predict`, and ZIP-producing `POST /api/tile` are implemented.
- Windowed tiling preserves output dimensions and source transform/CRS; three class scores plus class ID are written per window.
- Partial edges repeat values for model input, and writes crop to real dimensions.
- Dashboard upload/error/loading/download controls and a four-stage explicitly simulated timeline are included.
- Timeline stage feeds the same map and acreage analytics; uploads remain separate.

## Actual demonstrations

The artificial mosaic was 130 pixels wide and 97 pixels high, processed in six windows. Its stitched TIFF had shape 4 × 97 × 130. The recorded small run took approximately 0.25 seconds including model loading, excluding demonstration image creation and plotting. This is a tiny local demonstration, not a throughput benchmark. See `reports/week4/tiling_demo.json` and `tiling_demo.png`.

Live local API examples returned HTTP 200 for a real dataset patch and for the artificial tiled mosaic. The download contained `predictions.tif` and `summary.json`, with six tiles and dimensions 97 × 130. Responses are recorded in `reports/week4/api_demo.json`.

The 19-cell notebook executed, including a fresh temporary tiling run and two image outputs. TypeScript checking and the production frontend build passed. Vite retains the existing large JavaScript bundle warning. No separate automated test suite, failure-case campaign or load benchmark was added or run. Live browser interactions and Mapbox rendering were not visually verified.

## Limits to state during the internship review

The TIFF contains repeated patch scores, not a learned pixel-level segmentation. Synthetic mosaic coordinates and four timeline stages are invented. Real history, chemical abnormalities, three-week forecasting, general sensor transfer and verified farm mapping remain unsupported. Source georeferencing is preserved, not certified. CPU inference is implemented; GPU throughput is not claimed.

The API is intended for a single-worker local development setup, with 128 MiB and 256-tile limits. The CLI supports larger compatible rasters through its separate tile limit, but no giant-raster memory benchmark was performed. Model weights and previously reported validation accuracy were unchanged in Week 4.
