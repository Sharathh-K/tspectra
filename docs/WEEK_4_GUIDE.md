# Week 4 — API, tiling, and a clear dashboard

## The idea, explained like a puzzle

Imagine a huge picture that cannot fit on your desk. You cut it into small squares, look at one square at a time, write down an answer, and put the answers back in their original positions.

That is **tiling**. The **API** is a small reception desk: you give it a TIFF, it asks the saved model for predictions, and it gives you a result. The dashboard is the friendly form you use to talk to that reception desk.

The screenshot also asks for a timeline. Our ZIP does not contain verified dates for repeated observations of the same farm. We therefore provide four clearly invented stages to demonstrate the slider. They are not historical measurements or forecasts.

## What we reuse

The Week 3 model, its numeric scaling/PCA recipe, and its three classes: Health, Other, Rust. There is no new model training in Week 4. The mid-project audit already checked all 900 TIFFs against the supplied ZIP; Week 4 operates on those same compatible patch data.

A file must have the same band order and value scale as training: 125 spectral bands, optionally followed by the observed binary 0/65535 extra band. Matching the band count alone does not establish compatibility with a different satellite or sensor. RGB images and generic 200-band cubes are not interchangeable inputs.

## 1. API: the reception desk

From the repository root, open a VS Code terminal:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m uvicorn terraspectra.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Leave this terminal running. Open a second terminal for the frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

Restart an already running frontend after the new Vite proxy configuration is pulled. Vite forwards `/api` requests to port 8000. Open the displayed dashboard URL and choose **Week 4 inference**. The diagram and simulation work without a Mapbox token. Satellite tiles still require your public token.

API documentation is at `http://127.0.0.1:8000/docs`. Health information is at `http://127.0.0.1:8000/api/health`.

| Route | Send | Receive |
|---|---|---|
| GET `/api/health` | Nothing | Ready status and limits |
| POST `/api/predict` | One 64×64 TIFF as raw bytes | JSON patch scores and metadata |
| POST `/api/tile` | Compatible TIFF as raw bytes | ZIP containing `predictions.tif` and `summary.json` |

Send raw TIFF bytes with `Content-Type: application/octet-stream`. Do not send a path string, JSON or multipart form. The frontend handles this automatically.

Example in another terminal:

```bash
curl --fail-with-body -H 'Content-Type: application/octet-stream' \
  --data-binary '@data/raw/train/Health/hyper (1).tif' \
  http://127.0.0.1:8000/api/predict
```

For a tiled download, replace the route with `/api/tile` and add `--output predictions.zip`. Use a fresh output filename.

### Keep laptop use bounded

The service loads the model once at startup. It streams uploads into a temporary file, rather than storing the whole body in a Python bytes object. Model work runs in a worker thread so the async request handler is not doing the CPU computation itself. One upload/inference is accepted at a time; another receives HTTP 429. Run **one server worker**, as documented; each extra worker would have its own model and admission state.

Limits are 128 MiB uploaded bytes and 256 tiles. Oversized uploads receive 413; invalid TIFFs or unsupported dimensions/bands/nodata receive 422. Files are decoded only as TIFFs. Temporary input/output files are removed after a JSON response, failure, or completed ZIP download. A cancelled browser request may not immediately stop CPU work already running.

This is a local CPU demonstration service, not a high-throughput GPU or public deployment. Vite's proxy applies to development; a separately hosted production frontend needs a configured reverse proxy for `/api`. No remote cloud deployment is included.

## 2. Tiling: cut, classify, put back

The model expects 64×64 patches. The algorithm walks across the image in 64-pixel steps without overlap:

1. Read one Rasterio window, with bands first.
2. Reject masked, nodata or non-finite values instead of guessing their meaning.
3. Verify and drop the optional binary extra band.
4. If the window is smaller at the right/bottom edge, repeat its edge values to reach 64×64.
5. Apply the **saved** scaler and PCA; never refit them on an upload.
6. Pool spatially using the same Week 2/3 helper and run the saved transformer.
7. Repeat the resulting three class scores and class ID across the window's real pixels.
8. Write that window to disk immediately, cropping away padded rows/columns.

Why repeat the answer? The model learned a label for an entire patch. It did not learn pixel masks. Repeating a patch score produces a block map that can be stitched back, but it does **not** create genuine pixel-level disease segmentation. Blocks may have visible seams; no overlap blending or seam-removal claim is made. Padding is a computational convenience with unvalidated effects on edge accuracy.

The output TIFF has four float32 bands:

1. Health score
2. Other score
3. Rust score
4. Class ID: 0 Health, 1 Other, 2 Rust

Scores are uncalibrated softmax outputs. The class-ID band is float32 for a common TIFF datatype, although its values are integer IDs. Source width, height, affine transform and CRS are preserved. Copying unknown metadata does not validate real geographic placement. Original arbitrary tags and masks are not copied as scientific truth.

## 3. Larger local inputs

Use the command-line path for compatible files too large for the upload limit:

```bash
PYTHONPATH=src python -m terraspectra.tiling "/path/to/compatible.tif" data/outputs/predictions.tif
```

This writes a TIFF and a JSON summary. Outputs must have a new filename. The default CLI limit is 4,096 tiles; change it deliberately with `--max-tiles`. The model processes one tile at a time, but GDAL's source block layout also affects real memory and disk reads. An enormous compressed strip can require larger internal reads than a small window suggests. The code sets a 32 MiB GDAL cache; that is not a hard cap on total process memory. JSON metadata grows with the number of tiles, and disk space is needed for the output.

No giant-satellite-raster benchmark has been performed. Band compatibility, calibration, physical resolution and trustworthy georeferencing remain requirements before applying this model outside the supplied dataset.

## 4. Refine and polish

- Four-stage **simulated timeline** changes invented cell scores by fixed factors: 0.6, 0.8, 1.0, 1.15, capped at 1. No dates are invented.
- The map, selected-cell display and acreage analytics use the same selected stage. Changing stage clears stale cell selection.
- The score slider filters the current stage; whole-grid charts reflect that stage too.
- The inference form shows loading, error and success states, disables duplicate submissions, offers cancellation and provides a ZIP download.
- Predictions from uploaded files stay separate from the synthetic map because no reliable geographic link exists.
- Native sliders, labels, keyboard-accessible controls and live status messages support understandable interaction. Browser visual/accessibility review remains separate from successful compilation.

## 5. Walk through the demonstration notebook

Open `notebooks/05_week_four_api_and_tiling.ipynb` in VS Code and select `.venv`. It explains windows, padding, output bands, API requests and simulation stages. It creates a temporary 130×97 artificial mosaic from dataset patches to demonstrate six windows, including thin right/bottom edges. Its assigned coordinates are explicitly synthetic, not the patches' true origin.

The tiny report and figure are in `reports/week4`; large temporary TIFFs and user outputs are not committed. Reproduce the demonstration with:

```bash
PYTHONPATH=src python -m terraspectra.week4_demo
```

Read [the delivery record](WEEK_4_RESULTS.md) for actual examples and verification limits.

## Mentor handoff

Say: “I exposed the trained classifier through a local API, processed compatible TIFFs window by window, and stitched patch scores back to a raster with the original dimensions. I demonstrated timeline controls using labelled synthetic stages because the dataset cannot establish a real history.”

The remaining unsupported claims are unchanged: chemical diagnosis, validated real-farm disease maps, three-week early forecasting, pixel segmentation and high-throughput GPU inference.
