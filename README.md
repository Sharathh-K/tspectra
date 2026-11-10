# TerraSpectra — Week 1

Hyperspectral wheat image preparation and a React / Mapbox / Deck.gl map scaffold.
Built for the Week 1 tasks in the internship plan supplied by Sharath.

**Start with [the plain-language approach](docs/WEEK_1_GUIDE.md), then run
[the explained notebook](notebooks/01_week_one_data_preparation.ipynb).**

## What is included

- Actual ZIP inspection, extraction, labels, file inventory and a repeatable split.
- Rasterio loading and verified removal of a binary extra band in 159 TIFFs.
- Training-only scaling and PCA: 125 useful bands become 16 components.
- Saved preprocessing recipe and compact arrays for Week 2.
- A separate synthetic 224-band GeoTIFF exercise for the plan's mock-data requirement.
- React 18 + TypeScript dashboard, Mapbox satellite map and synchronized Deck.gl boundary.
- A 19-cell notebook with simple explanations and visual examples.

This is data preparation and map scaffolding. Disease model training is Week 2.

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

Open the local address printed by Vite (normally `http://127.0.0.1:5173`). A placeholder
appears when the token is absent. The satellite basemap requires your token and an
internet connection. Restart Vite after changing `.env.local`.

Drag to pan, scroll to zoom, and use the navigation control or right-drag to tilt /
rotate. Toggle **Demo boundary** and press **Reset view**. The Deck.gl polygon stays
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
src/terraspectra/prepare.py          # The complete, small real-data pipeline
src/terraspectra/make_mock_cube.py   # Separate synthetic format exercise
notebooks/01_week_one_data_preparation.ipynb
frontend/src/App.tsx                # Dashboard shell and preparation summary
frontend/src/FarmMap.tsx            # Mapbox and Deck.gl connection
frontend/src/farm.ts                # Clearly marked synthetic farm polygon
docs/WEEK_1_GUIDE.md                # Child-friendly explanation and review notes
docs/VALIDATION.md                  # Checks performed and remaining limits
```

## Git handoff

Work is in branch `codex/week-one-foundation` in the local clone. Data, environments,
Mapbox local settings, processed arrays and fitted binary files are ignored. No code
has been pushed to GitHub. Review with `git status` and `git diff` in VS Code, then
commit and push when ready. The reports and notebook are small enough to review in
Git. Do not add the ZIP or raw dataset to the public repository.
