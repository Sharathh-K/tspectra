# Reconciliation with the supplied project screenshots

This pass reviewed the two supplied screenshots against the existing source, milestone guides and recorded evidence. It does not reinterpret ambitious scientific outcomes as completed merely because interface controls exist.

| Milestone | Implementation and location | Remaining boundary |
|---|---|---|
| Preparation | Rasterio TIFF inventory; train-only scaling/PCA; real 125-band data and separate synthetic 224-band exercise; Data quality page now includes real-sample spectra | No real 200+ band satellite validation or HDF5-specific ingestion exercise |
| Map foundation | React, Mapbox GL JS and Deck.gl synchronized overlay | Fictional farm; token needed for satellite imagery |
| CNN and heatmap | Trained compact 3D–2D CNN; 80-cell mock JSON grid, controls and selection | Patch Health/Other/Rust categories, not chemical-stress pixel masks |
| Extraction/memory audit | All-file fingerprints and processed arrays; recorded fresh-process CPU batch trials | Not giant-cube or GPU capacity proof |
| GIS validation | Independent geometric checks on synthetic grid | Real farm GPS registration not validated |
| Transformer | Saved CNN + spatial-token transformer, measured comparison | One development split; no original-band attention explanation |
| Analytics | Score bins, threshold-selected acreage, real model comparison | Chemical anomalies and actual disease acreage unavailable |
| API and tiling | Saved model served by FastAPI; windowed raster reads/writes; edge handling and ZIP output; new explicit service check | CPU/local bounded service; patch scores repeated within windows |
| Timeline and polish | Four invented stages; separate responsive workspaces; new in-app guide and downloadable manual | No real dated progression or three-week forecasts |
| Final presentation | Documentation, notebooks, evidence records and GitHub source; new spectral explorer and examples | Educational prototype, not a validated agricultural decision system |

## Decisions in this update

- Preserve working models, preprocessing and measured metrics; no retraining is necessary for a dashboard/documentation update.
- Add six source-traceable false-colour previews and whole-patch mean spectra. Use band index and sensor units rather than unsupported wavelength/reflectance labels.
- Add practical help alongside inference, an on-demand readiness check and a separate Dashboard guide view.
- Retain feature names in dashboard navigation, as requested; week names remain in learning documents only.
- Do not attach unlocated Kaggle predictions to the invented farm, invent chemical concentrations, or display a forecast as established science.

## Research used to review the design

1. [Rasterio windowed reads/writes](https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html): windows enable subset processing, but underlying storage blocks influence the amount read. Therefore tiling alone does not prove a fixed total-memory ceiling.
2. [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): fitting transformations on training data helps prevent leakage. Retain the saved train-only scaler/PCA; do not refit on uploads or validation data.
3. [Deck.gl MapboxOverlay](https://deck.gl/docs/api-reference/mapbox/mapbox-overlay): the overlay synchronizes rendering with the map. Camera synchronization is distinct from proving geographic accuracy of input coordinates.
4. [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/): shared resources such as models can be loaded at startup. Keep the existing model lifespan and add an explicit UI health check rather than reload per prediction.
5. [PyTorch TransformerEncoderLayer](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html): attention and feedforward blocks support the compact token-processing design. Documentation does not substantiate disease-specific performance; the repository's measurements do.
6. [ESA Sentinel-2](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/): Sentinel-2 has 13 multispectral bands. The brief's mention of Sentinel must not be treated as proof of a 200+ band hyperspectral source compatible with this classifier.

Research reviewed on 11 November 2026. These are conceptual references; this update does not change the installed dependency versions. See the existing research documents for HybridSN/ViT architecture references and the final evidence report for measured local results.
