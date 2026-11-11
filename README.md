# Week 4 added: local API, tiling and simulated timeline

Read [the Week 4 guide](docs/WEEK_4_GUIDE.md), [notebook](notebooks/05_week_four_api_and_tiling.ipynb), and [research](docs/WEEK_4_RESEARCH.md). Start the local API on port 8000, restart the frontend, and open **Week 4 inference**. Large TIFF outputs stay local.

# Week 3 added: transformer and analytics

Start with [the Week 3 guide](docs/WEEK_3_GUIDE.md), [notebook](notebooks/04_week_three_transformer.ipynb), and [research](docs/WEEK_3_RESEARCH.md). The dashboard compares real model results and provides separately labelled simulated acreage analytics.

# Mid-project review added

Start with [the review guide](docs/MID_PROJECT_REVIEW.md), [the notebook](notebooks/03_mid_project_review.ipynb), and [the research notes](docs/MID_PROJECT_RESEARCH.md). The dashboard now includes extraction, CPU memory, and synthetic grid validation results. Real-farm registration and live browser alignment remain unverified.

# TerraSpectra — Weeks 1 and 2

Hyperspectral wheat image preparation, a compact trained 3D–2D CNN, and a React /
Mapbox / Deck.gl dashboard with a clearly simulated heatmap. Built for the first
two weeks of the internship plan supplied by Sharath.

**Week 2:** start with [the simple model and heatmap guide](docs/WEEK_2_GUIDE.md),
then open [the executed Week 2 notebook](notebooks/02_week_two_model_and_heatmap.ipynb).
The [research notes](docs/WEEK_2_RESEARCH.md) explain the architectural choices.

**Week 1:** [data-preparation guide](docs/WEEK_1_GUIDE.md) and
[executed notebook](notebooks/01_week_one_data_preparation.ipynb) remain available.

## What is included

- Actual ZIP inspection, extraction, labels, file inventory and a repeatable split.
- Rasterio loading and verified removal of a binary extra band in 159 TIFFs.
- Training-only scaling and PCA: 125 useful bands become 16 components.
- Saved preprocessing recipe and compact arrays for Week 2.
- A separate synthetic 224-band GeoTIFF exercise for the plan's mock-data requirement.
- React 18 + TypeScript dashboard, Mapbox satellite map and synchronized Deck.gl boundary.
- A 19-cell notebook with simple explanations and visual examples.

## Week 2 — completed model and heatmap

- A 23,703-parameter PyTorch hybrid 3D–2D CNN, plus a logistic regression baseline.
- Real training, saved weights, portable numeric PCA/scaler parameters and predictions.
- A clickable 80-cell mock heatmap with visibility, opacity, score filter and legend.
- A working diagram preview without a token; Mapbox satellite overlay with your token.
- A second explained notebook, research notes, checks and a model card.

| Recorded development result | CNN | Logistic baseline |
| --- | --- | --- |
| Accuracy on 120 labelled patches | 65.8% | 64.2% |
| Macro F1 | 0.635 | 0.645 |

The CNN has higher accuracy but lower macro F1. Health recall is only 30%.
These are modest **development** results; the same set selected the checkpoint.
No independent test or new-farm performance has been established.

The measured run took 55.1 seconds on CPU after imports, used about 313 MiB peak
process memory during training/evaluation, ran 16 epochs and saved epoch 11.
Your runtime can differ. The model and preprocessing files total about 140 KB,
so you can inspect results and predict a patch without retraining.

From the repository root, after installing the updated requirements:

```bash
# Optional: repeat training using the Week 1 prepared data.
PYTHONPATH=src python -m terraspectra.train --epochs 20 --batch-size 16 --patience 5 --device cpu

# Predict one original dataset TIFF using the supplied model and PCA recipe.
PYTHONPATH=src python -m terraspectra.predict "data/raw/train/Health/hyper (1).tif"

# Optional: regenerate the independent, simulated frontend response.
PYTHONPATH=src python -m terraspectra.make_mock_heatmap
```

The model classifies **Health / Other / Rust patches**. The dataset has no chemical
stress labels or pixel infection masks. Map cells and scores are invented; model
predictions are not attached to those invented coordinates. See
[Week 2 validation](docs/WEEK_2_VALIDATION.md) and [model card](models/week2/MODEL_CARD.md).

Training overwrites the Week 2 artifacts. Preserve the supplied model/recipe as a
pair if you want to compare runs. Full-image tiling and API integration are Week 4;
the transformer is Week 3.

## 1. Open in VS Code and install Python dependencies

Use Python 3.10 or newer for a fresh setup (this delivery also ran on the available
Python 3.9 environment). From the cloned repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name terraspectra --display-name "TerraSpectra (.venv)"
```

Install the VS Code Python and Jupyter extensions. Open the notebook and select
**TerraSpectra (.venv)** as its kernel. If you move the folder, recreate its virtual
 environment and kernel rather than copying the old environment.

## 2. Prepare the downloaded data

The download is from [Beyond Visible Spectrum: AI for Agriculture 2023](https://www.kaggle.com/competitions/beyond-visible-spectrum-ai-for-agriculture-P1/data).
Accept Kaggle's competition rules yourself before using the data. The dataset's
terms apply; it is not relicensed by this repository.

On your Mac, the provided archive is at this path:

```bash
python src/terraspectra/prepare.py --zip "$HOME/Downloads/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

The command is repeatable: it skips already extracted files with matching sizes,
then rebuilds reports and PCA outputs. It reads one image at a time and samples at
most 64 pixels per training image for PCA. On another machine, replace the ZIP path.
If TIFFs are already in `data/raw`, simply run:

```bash
python src/terraspectra/prepare.py
```

Expected split: 480 training, 120 development-validation and 300 unlabelled images.
The original `val/val` folder has no class labels. The inventory maps the labelled
files to Health=0, Other=1, Rust=2. Raw 126-band files must have a binary final
0/65,535 plane before that plane is removed.

Outputs:

| Path | Purpose |
| --- | --- |
| `data/raw/` | Original extracted TIFFs, about 925 MB |
| `data/processed/` | PCA arrays, about 236 MB total, H × W × 16 float32 |
| `reports/inventory.csv` | Paths, labels, splits, shapes, metadata and fingerprints |
| `reports/preprocessing.joblib` | The fitted scaler and PCA for reuse |
| `reports/dataset_summary.json` | Counts and measured PCA variance |
| `frontend/public/dataset-summary.json` | The dashboard's real data summary |

Allow a few GB for data and dependencies. This pipeline does not download INRAE or
require a GPU. Keep your original ZIP until you are satisfied with extraction.
Only load `.joblib` files you created or trust.

## 3. Run the notebook

Open `notebooks/01_week_one_data_preparation.ipynb` in VS Code and run it from top to
bottom after preparing the data. It includes TIFF inspection, a spectral curve,
three-band previews, PCA variance, a check against saved output, a synthetic mock
cube exercise and an explanation of the map code. The supplied notebook includes
outputs from the local dataset so you can review it immediately.

## 4. Start the map dashboard

Install Node.js 22 LTS if you do not already have Node. From this repository:

```bash
cd frontend
npm install
cp .env.example .env.local
```

Open `.env.local` and replace the example with your own **public** Mapbox token:

```text
VITE_MAPBOX_TOKEN=pk.your_actual_public_token
```

Obtain a token from your Mapbox account. Frontend tokens are visible to browsers;
use a public token, limit its allowed URLs as appropriate, and never paste a secret
token here. Mapbox account conditions and usage charges apply.

```bash
npm run dev
```

Open the local address printed by Vite (normally `http://127.0.0.1:5173`). An interactive simulated heatmap diagram
appears when the token is absent. The satellite basemap requires your token and an
internet connection. Restart Vite after changing `.env.local`.

Drag to pan, scroll to zoom, and use the navigation control or right-drag to tilt /
rotate. Toggle **Farm boundary** or **Show heatmap**, adjust opacity or minimum score, select
a cell and press **Reset view** when the satellite map is active. The Deck.gl polygon stays
aligned with Mapbox through `MapboxOverlay`.

For a production build:

```bash
npm run build
```

The delivery also includes `pnpm-lock.yaml`; for the exact dependency graph used
here, use pnpm and `pnpm install --frozen-lockfile` instead of npm. Use one package
manager consistently. A normal npm install will create its own lockfile.

## 5. Understand the boundaries of the result

- Real useful input is 125 bands, not the plan's aspirational 200+.
- The practice farm boundary near Bengaluru is invented and independent of the images.
- Unknown TIFF CRS metadata is recorded; it is not treated as trustworthy geography.
- There is no verified real farm location, pixel infection mask or chemical diagnosis.
- A patch split is a development check, not proof of performance on unseen farms.
- PCA retained variance is not classification accuracy. No three-week forecast is claimed.

## Files to read first

```text
src/terraspectra/model.py            # Small hybrid 3D–2D CNN
src/terraspectra/data.py             # Reuse the Week 1 split and shrink spatial input
src/terraspectra/train.py            # Baseline, bounded training, reports and weights
src/terraspectra/predict.py          # Raw TIFF to patch-class scores
src/terraspectra/prepare.py          # The complete, small real-data pipeline
src/terraspectra/make_mock_cube.py   # Separate synthetic format exercise
notebooks/01_week_one_data_preparation.ipynb
frontend/src/App.tsx                # Dashboard shell and preparation summary
frontend/src/FarmMap.tsx            # Mapbox and Deck.gl connection
frontend/src/farm.ts                # Clearly marked synthetic farm polygon
docs/WEEK_1_GUIDE.md                # Child-friendly explanation and review notes
docs/VALIDATION.md                  # Historical Week 1 checks
docs/WEEK_2_GUIDE.md                # Model and heatmap explained simply
docs/WEEK_2_RESEARCH.md             # Sources and decisions
docs/WEEK_2_VALIDATION.md           # Current checks and limitations
```

## Checks

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
cd frontend
npm test
npm run build
```

Frontend tests use Node.js 22.6+ with TypeScript stripping. Python artifact tests
use the supplied model and local Week 1 prepared data; raw-data checks skip when
that data is absent. Tests cover model gradients, tensor axes, preprocessing parity,
saved predictions, mock geometry, invalid responses and fixed colour boundaries.

## Git handoff

Weeks 1 and 2 are published to `main`. The source, executed notebooks, reports,
small trained model and numeric preprocessing recipe are tracked. Raw data,
processed arrays, virtual environments, installed packages and local credentials
are ignored. Pull `main` in VS Code to receive updates:

```bash
git pull --ff-only origin main
```

The [source data](https://www.kaggle.com/competitions/beyond-visible-spectrum-ai-for-agriculture-P1/data)
retains its competition terms. No dataset is redistributed in this repository.
