# TerraSpectra

An educational hyperspectral crop-patch classifier, local tiled-inference API, and simulated geospatial dashboard.

**Start here:** [Final review](docs/FINAL_REVIEW.md) · [Final notebook](notebooks/06_final_review.ipynb) · [Mentor walkthrough](docs/MENTOR_WALKTHROUGH.md) · [Research](docs/FINAL_RESEARCH.md)

**Dashboard help:** [User guide with examples](docs/DASHBOARD_GUIDE.md) · [Requirements reconciliation and research](docs/REQUIREMENTS_RECONCILIATION.md)

## What it does

- Prepares 900 TIFF patches: 125 usable spectral bands → 16 PCA components.
- Classifies Health / Other / Rust using saved compact CNN and CNN–transformer models.
- Serves local TIFF predictions through FastAPI and stitches tile scores into output rasters.
- Provides separate **Overview**, **Map & analytics**, **Inference**, **Model performance**, **Data quality**, and **Dashboard guide** pages.
- Includes six real-sample false-colour previews and an interactive 125-band mean-signal explorer.
- Shows explicitly simulated farm scores, acreage and four timeline stages.

The transformer achieved **70.8% accuracy / 0.707 macro F1** on 120 development-validation patches. Those examples also selected the checkpoint; this is not independent test performance. Chemical diagnosis, verified farm disease mapping and three-week forecasting are unsupported. Tiled scores are patch classifications, not pixel segmentation.

## Run in VS Code

Open this repository folder. Use the existing `.venv`, or create one:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Exact versions used for the delivered scientific results are in `requirements-reproduced.txt`. The recorded environment was macOS/Python 3.9.6/PyTorch 2.8.0; package availability varies by platform. CPU inference is the default.

### Start the API

```bash
PYTHONPATH=src python -m uvicorn terraspectra.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Saved weights and preprocessing are included, so this does not require retraining. API documentation: `http://127.0.0.1:8000/docs`.

### Start the dashboard in another terminal

Use a current supported Node.js installation and pnpm (Node 22+ is suitable for the repository's optional test command).

```bash
cd frontend
pnpm install
pnpm dev
```

Open the printed local URL. Vite proxies `/api` to port 8000. Restart Vite after configuration changes. Routes use `#/overview`, `#/map`, `#/inference`, `#/models`, and `#/data`; only the selected page appears. A production host would need its own `/api` reverse proxy.

For satellite imagery, create `frontend/.env.local` with `VITE_MAPBOX_TOKEN=your_public_mapbox_token`, then restart Vite. Without a token, the interactive diagram remains available. Never commit private credentials; local environment files are ignored.

## Prepare the dataset when needed

The original ZIP and extracted/processed TIFF arrays are not included in Git. Keep the original dataset under its applicable access terms.

```bash
PYTHONPATH=src python -m terraspectra.prepare --zip "/Users/sharath/Downloads/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

Adjust the path on another computer. Preparation extracts TIFFs, builds the fixed split, and fits scaling/PCA on training data only. It consumes local disk space; do not repeat it just to browse the dashboard or use the saved inference model. The input ZIP contains roughly 925 MB of uncompressed files, plus prepared arrays and the ZIP itself.

## Main commands

```bash
# Optional retraining; existing artifacts already work.
PYTHONPATH=src python -m terraspectra.train --architecture hybrid_vit

# Predict a compatible dataset patch.
PYTHONPATH=src python -m terraspectra.predict "data/raw/train/Health/hyper (1).tif" --model-dir models/week3

# Tile a compatible larger raster; choose a fresh output filename.
PYTHONPATH=src python -m terraspectra.tiling "/path/to/compatible.tif" data/outputs/predictions.tif

# Reproduce final evidence checks with prepared data available.
PYTHONPATH=src python -m terraspectra.final_review --zip "/path/to/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

API uploads are limited to 128 MiB and 256 tiles. Inputs need compatible band ordering and radiometry, not merely 125 bands. Outputs retain source coordinates without certifying them. See [API and tiling details](docs/WEEK_4_GUIDE.md).

## Weekly internship write-ups

Four separate reports summarize the completed work, approach, recorded results and limitations:

1. [Week 1 — Data preparation and map foundation](docs/weekly-writeups/WEEK_1.md)
2. [Week 2 — Hybrid CNN and heatmap rendering](docs/weekly-writeups/WEEK_2.md)
3. [Week 3 — Vision Transformer and analytics](docs/weekly-writeups/WEEK_3.md)
4. [Week 4 — Inference API, tiling and interface polish](docs/weekly-writeups/WEEK_4.md)

## Learning materials

| Topic | Guide | Notebook |
|---|---|---|
| Preparation and map foundation | [Guide](docs/WEEK_1_GUIDE.md) | [01](notebooks/01_week_one_data_preparation.ipynb) |
| CNN and heatmap | [Guide](docs/WEEK_2_GUIDE.md) | [02](notebooks/02_week_two_model_and_heatmap.ipynb) |
| Extraction, memory and GIS audit | [Guide](docs/MID_PROJECT_REVIEW.md) | [03](notebooks/03_mid_project_review.ipynb) |
| Transformer and analytics | [Guide](docs/WEEK_3_GUIDE.md) | [04](notebooks/04_week_three_transformer.ipynb) |
| API, tiling and timeline | [Guide](docs/WEEK_4_GUIDE.md) | [05](notebooks/05_week_four_api_and_tiling.ipynb) |
| Final review and presentation | [Guide](docs/FINAL_REVIEW.md) | [06](notebooks/06_final_review.ipynb) |

Select the project `.venv` kernel in VS Code. Notebooks include saved outputs and beginner-friendly explanations; optional retraining/rescanning switches are off by default. Historical documents retain milestone names, while the dashboard uses feature names.

## Repository layout

- `src/terraspectra`: preparation, models, inference, API, audits.
- `frontend`: React, Mapbox and Deck.gl interface.
- `models`: small saved checkpoints and numeric preprocessing.
- `reports`: metrics, predictions, evidence and figures.
- `notebooks`, `docs`: explanations and reproducible walkthroughs.
- `data/raw`, `data/processed`, `data/outputs`: local ignored data.

See [final verification notes](docs/FINAL_VERIFICATION.md) for what was actually inspected and what remains unverified.
