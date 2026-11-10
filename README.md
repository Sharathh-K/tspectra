# TerraSpectra

**Hyperspectral crop disease forecasting: spot fungal blight weeks before the leaves show it.**

TerraSpectra ingests hyperspectral satellite data, runs a 3D-CNN + Vision Transformer model on it, and shows predicted disease risk as a heatmap on a 3D map dashboard. The goal is to let an agricultural analyst find a small at-risk zone (for example, 5 acres of a 1,000-acre farm) early enough to treat only that zone instead of the whole field.

> **Status:** early development. Everything below describes the design and plan; items are ticked off in the [Roadmap](#roadmap) as they are built.

---

## Problem

Standard satellite monitoring relies on RGB or a few infrared bands. By the time those images show yellowing or browning, the disease has already spread and the harvest is at risk.

Hyperspectral sensors capture 200+ narrow bands per pixel. Infection changes a plant's chlorophyll, water content and leaf structure, and these changes appear as small shifts in the reflected spectrum before any visible symptom. TerraSpectra trains a model to pick up those shifts.

## Use case

1. An analyst opens the dashboard for a 1,000-acre farm.
2. The backend processes the latest hyperspectral scene for that area.
3. The dashboard highlights a roughly 5-acre zone in red, predicting a fungal blight outbreak about three weeks before symptoms are visible.
4. The farm applies a targeted, preventative treatment to that zone only.

## Architecture

```
Hyperspectral scenes --> Data pipeline --> 3D-CNN + ViT --> Inference API --> GIS dashboard
(EnMAP, PRISMA, EMIT)    (Rasterio, GDAL)   (PyTorch)        (FastAPI, GPU)    (React, Deck.gl)
```

| Module | Stack | Responsibility |
|---|---|---|
| Geospatial data pipeline | Python, Rasterio, GDAL | Read large hyperspectral cubes, convert to surface reflectance, remove noisy water-absorption bands, mask non-crop pixels, extract patches |
| Model | PyTorch | 3D convolutions capture local spatial-spectral features; a Vision Transformer models relationships across the spectral bands; outputs healthy / at-risk / infected |
| Inference API | FastAPI | Accept a field boundary, tile the raster into chunks, run batched GPU inference, return a risk raster |
| Dashboard | React, Deck.gl | Render risk heatmaps over 3D terrain, let the analyst inspect flagged zones |

## Data

No single public dataset covers this task end to end, so the plan combines several sources. Check licences and availability before use.

| Purpose | Source |
|---|---|
| Model development and benchmarking | Indian Pines, Salinas, Pavia, WHU-Hi |
| Satellite hyperspectral scenes | EnMAP, PRISMA, NASA EMIT, DESIS, Hyperion archive (USGS EarthExplorer) |
| Time-series proxy | Sentinel-2 (multispectral, 13 bands) |
| Disease spectra | Leaf and canopy hyperspectral disease datasets from Zenodo, Mendeley Data, Kaggle, Figshare |
| Synthetic spectra | PROSPECT / PROSAIL simulation for augmentation and pretraining |
| Weather | ERA5, NASA POWER |
| Masks and terrain | ESA WorldCover, Copernicus DEM or SRTM |
| Ground truth | Field scouting records and agricultural trial data |

**Labels are the main bottleneck.** Early-warning labels are created retrospectively: once a plot shows symptoms, its earlier images are labeled as pre-symptomatic. This needs repeated field visits across multiple dates.

Rough data targets:

| Stage | Target |
|---|---|
| Proof of concept | About 500 labeled patches per class |
| Solid model | 3,000 to 5,000+ labeled patches across 2+ seasons and several fields |
| Forecasting | 8 to 12 acquisitions per season over 2 to 3 seasons |

## Modeling approach

- **Baselines first:** PCA + Random Forest / XGBoost, and a 2D CNN with bands as channels. The 3D-CNN + ViT hybrid has to beat these to justify its cost.
- **Pretraining:** pretrain on public benchmarks and on unlabeled scenes (masked band reconstruction), then fine-tune on labeled disease data, since a hybrid model will overfit a few thousand labels.
- **Validation:** split train and test by field or plot, never by random pixel, to avoid spatial leakage.
- **Metrics:** recall, F1 and PR-AUC per class, plus the lead time of correct early warnings. Accuracy alone is misleading because healthy samples dominate.
- **Forecasting:** combine spectral time series with weather (humidity, temperature, rainfall) to predict risk ahead of time.

## Planned structure

```
terraspectra/
├── data/            # raw and processed data (not committed; use DVC or similar)
├── pipeline/        # ingestion, calibration, band cleaning, patch extraction
├── models/          # baselines, 3D-CNN + ViT hybrid, training code
├── api/             # FastAPI inference service
├── dashboard/       # React + Deck.gl frontend
├── notebooks/       # exploration and experiments
├── tests/
└── README.md
```

## Getting started

```bash
git clone <your-repo-url>
cd terraspectra
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Running instructions for the pipeline, API and dashboard will be added as each module lands.

## Roadmap

- [ ] Data pipeline: read scenes, reflectance conversion, band cleaning, field masking, patch extraction
- [ ] Baseline models and group-based evaluation
- [ ] 3D-CNN + ViT hybrid model
- [ ] Pretraining on public benchmarks and unlabeled scenes
- [ ] FastAPI inference service with tiled GPU processing
- [ ] React + Deck.gl dashboard with risk heatmaps
- [ ] Weather-aware forecasting
- [ ] Field validation against scouting data

## Known limitations

- **Sensor availability:** Hyperion stopped operating in 2017 and Sentinel-2 is multispectral, not hyperspectral. Live hyperspectral data comes from missions such as EnMAP, PRISMA and EMIT.
- **Resolution:** at about 30 m per pixel, a 5-acre zone is roughly 22 pixels, and mixed pixels (soil plus leaf) will reduce sensitivity.
- **Revisit and clouds:** hyperspectral satellites revisit less often than multispectral ones, and cloud cover can remove acquisitions.
- **Early-warning claims:** the three-week lead time is a target, not a result. It has to be demonstrated on labeled time-series data.

## Tech stack

Python, NumPy, Pandas, scikit-learn, PyTorch, Rasterio, GDAL, xarray, geopandas, FastAPI, Docker, React, Deck.gl, MapLibre or Mapbox, Git, DVC, MLflow or Weights & Biases.

## License

To be decided.