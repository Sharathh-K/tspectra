# TerraSpectra

**Hyperspectral Crop Disease Forecasting**

> Detect crop disease *weeks before* it becomes visible, using hyperspectral satellite data, a 3D-CNN + Vision Transformer model, and an interactive 3D GIS dashboard.

**Domain:** Precision Agriculture & Advanced Computer Vision

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Use Case](#use-case)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Team](#team)
- [Acknowledgements](#acknowledgements)

---

## Problem Statement

Traditional satellite crop monitoring relies on standard RGB or simple infrared imagery. Models built on these inputs only detect crop diseases **after** the leaves turn yellow or brown, which is too late to save the harvest. Standard 2D Convolutional Neural Networks (CNNs) also cannot process the massive spectral depth of data needed for early detection.

## Use Case

An agricultural analyst monitors a 1,000-acre farm through the TerraSpectra dashboard.

1. The system ingests **hyperspectral satellite data**, which captures 200+ bands of light invisible to the human eye.
2. The backend **3D-CNN + Vision Transformer** model analyzes subtle chemical changes in the plants' chlorophyll reflection.
3. The dashboard highlights a specific 5-acre zone in red, predicting a fungal blight outbreak **three weeks before** any visible symptoms appear.
4. The analyst can then apply hyper-targeted, preventative pesticide treatment instead of spraying the whole farm.

## Key Features

- **Geospatial data pipeline** that ingests and normalizes multi-gigabyte hyperspectral data cubes (e.g., NASA Hyperion, ESA Sentinel missions).
- **Hybrid 3D-CNN + ViT model** where 3D convolutions capture spatial-spectral features and a Vision Transformer models long-range correlations across spectral bands.
- **Scalable inference API** that tiles massive satellite rasters into chunks, runs them on GPU, and stitches the results back together.
- **3D GIS dashboard** rendering predicted disease heatmaps over satellite topography, with analytics and a historical timeline.

## System Architecture

```
┌──────────────────────┐   ┌────────────────────────┐   ┌───────────────────────┐
│  Hyperspectral Data  │   │   ML Engineering       │   │  Inference API        │
│  (HDF5 / GeoTIFF)    │──▶│  Rasterio + GDAL + PCA │──▶│  FastAPI + Tiling     │
│  NASA / ESA          │   │  3D-CNN + ViT (PyTorch)│   │  (GPU inference)      │
└──────────────────────┘   └────────────────────────┘   └───────────┬───────────┘
                                                                    │ JSON
                                                                    ▼
                                                        ┌───────────────────────┐
                                                        │  GIS Dashboard        │
                                                        │  React + Deck.gl      │
                                                        │  + Mapbox             │
                                                        └───────────────────────┘
```

## Tech Stack

| Layer | Technologies |
|---|---|
| Data pipeline | Python, Rasterio, GDAL, NumPy, scikit-learn (PCA) |
| Machine learning | PyTorch (3D-CNN, Vision Transformer) |
| Backend API | FastAPI, Uvicorn |
| Frontend | React, Deck.gl, Mapbox |
| Data formats | HDF5, GeoTIFF |

## Project Structure

> Suggested layout. Adjust it to match the actual repository.

```
tspectra/
├── backend/
│   ├── data/            # Data loading, preprocessing, PCA
│   ├── models/          # 3D-CNN, ViT, hybrid model
│   ├── training/        # Training and evaluation scripts
│   ├── api/             # FastAPI app and tiling logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/  # Map, heatmap layer, analytics panel
│   │   └── App.jsx
│   └── package.json
├── data/                # Sample / mock hyperspectral cubes (not committed if large)
├── docs/
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- GDAL installed on your system (required by Rasterio)
- A CUDA-capable GPU (recommended for training and inference)
- A [Mapbox access token](https://www.mapbox.com/) for the dashboard

### 1. Clone the repository

```bash
git clone https://github.com/Sharathh-K/tspectra.git
cd tspectra
```

### 2. Create your own branch

Each team member works on their own branch. Never push directly to `main`.

```bash
git checkout -b yourname-task
```

### 3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

Create a `.env` file in `frontend/`:

```
VITE_MAPBOX_TOKEN=your_mapbox_token_here
```

## Usage

**Run the inference API:**

```bash
cd backend
uvicorn api.main:app --reload
```

The API docs will be available at `http://localhost:8000/docs`.

**Run the dashboard:**

```bash
cd frontend
npm run dev
```

**Train the model:**

```bash
cd backend
python -m training.train --config configs/default.yaml
```

> Commands above are placeholders. Update the paths and flags once the code is in place.

## Roadmap

| Week | ML Engineering & Data Pipeline | Frontend & GIS |
|---|---|---|
| **Week 1** | **Data preparation:** parse mock hyperspectral cubes (HDF5/GeoTIFF) with Rasterio; apply PCA to reduce the 200+ spectral bands | **Map scaffolding:** build the React app; integrate Deck.gl and Mapbox to render base farm layers |
| **Week 2** | **Model architecture:** build the hybrid 3D-CNN in PyTorch; train it to classify healthy vs. chemically stressed pixels | **Heatmap rendering:** build UI components that overlay colored pixel grids on the 3D map from mock backend JSON |
| **Mid-Project Review** | **Extraction audit:** prove the pipeline handles the memory demands of 3D tensor batches during training | **GIS validation:** ensure the Deck.gl overlay aligns with real-world GPS coordinates |
| **Week 3** | **Vision Transformer:** add self-attention to capture complex correlations across spectral bands | **Analytics panel:** sidebar charts for total acreage at risk and specific chemical anomalies |
| **Week 4** | **API & tiling:** wrap the model in FastAPI; implement tiling to slice large satellite images and stitch results | **Refine & polish:** timeline sliders to show the historical progression of crop spectral health |
| **Final Review** | A fusion of geospatial data engineering and multi-dimensional deep learning | A professional, visually striking agricultural intelligence platform |

### Status

- [ ] Week 1: Data preparation and map scaffolding
- [ ] Week 2: Model architecture and heatmap rendering
- [ ] Mid-project review
- [ ] Week 3: Vision Transformer and analytics panel
- [ ] Week 4: API, tiling and polish
- [ ] Final review

## Contributing

1. Make sure you have been added as a collaborator on the repository.
2. Create your own branch: `git checkout -b yourname-task`
3. Commit your work with clear messages: `git commit -m "Add PCA preprocessing"`
4. Push your branch: `git push -u origin yourname-task`
5. Open a **Pull Request** into `main` for review.

## Team

| Name | Role |
|---|---|
| _Your name_ | _ML Engineering / Frontend & GIS_ |
| _Teammate_ | _Role_ |

## Acknowledgements

- NASA Hyperion and ESA Sentinel missions for hyperspectral data sources
- Rasterio, GDAL, PyTorch, FastAPI, React, Deck.gl and Mapbox communities

---

_This project is under active development as part of an internship project._
