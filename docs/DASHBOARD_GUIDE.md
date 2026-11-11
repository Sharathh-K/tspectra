# TerraSpectra dashboard — user guide

## 1. What you are looking at

TerraSpectra has two connected learning goals: classify real hyperspectral image patches, and demonstrate how geographic crop-health information could be explored. The model evidence uses real Kaggle data. The farm grid, its scores and its timeline are simulated. Uploaded predictions are not assigned to that fictional farm.

Imagine a picture as a book: every pixel has 125 pages of light measurements. Preprocessing makes 16 summary pages. A CNN finds patterns, a transformer lets image regions exchange information, and the model chooses Health, Other or Rust for the entire patch.

## 2. Start the application

From the repository folder, activate the installed environment and start the API:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m uvicorn terraspectra.api:app --host 127.0.0.1 --port 8000 --workers 1
```

In a second terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

Open the local address printed by Vite. Saved weights are included, so retraining is unnecessary. Dataset files are not committed: keep the downloaded ZIP locally and prepare it only if you need the raw/processed files. Follow the README for environment installation.

To enable satellite tiles, set `VITE_MAPBOX_TOKEN` to your public token in `frontend/.env.local`, then restart Vite. Without a token the labelled diagram is available. Satellite rendering also needs internet and WebGL. Mapbox setup does not establish the true location of the Kaggle patches.

## 3. Overview

The three cards show 900 image patches, 125 usable bands and 16 PCA components. These are dataset/preprocessing counts, not farm acreage or disease detections. Use the workspace cards or navigation links to move between views. The guided walkthrough provides a short route through the application.

**Example:** 900 files does not mean 900 labelled training examples. There are 480 training, 120 development-validation and 300 unlabelled patches.

## 4. Data quality and spectral explorer

The preparation panel explains scaling and PCA. Scaling learns band averages and spreads from training samples only; PCA also learns from training samples only. Retained variance describes how much variation PCA preserves, not the proportion of correct predictions.

The spectral explorer lets you choose two examples from each folder class. Its 64 × 64 previews map bands 90, 60 and 30 to RGB. Each preview is stretched separately for visibility. The accompanying curve is the mean signal over all pixels for each of 125 bands. All six examples share the same vertical axis. Use the band slider to read a value precisely.

**Example:** choose “Rust · example 1,” then move the slider to band 60. The displayed number is the average raw sensor value at that band. It is not a rust concentration. The folder name is the supplied label, not the model's prediction. Pink in the preview is not automatically diseased tissue.

The horizontal axis is band index, because an exact wavelength calibration was not supplied. The curve includes background pixels and does not isolate leaves. Export provenance records source paths and SHA-256 hashes in `frontend/public/explorer/samples.json`. Regenerate the small assets locally with:

```bash
PYTHONPATH=src python -m terraspectra.export_explorer --zip "/path/to/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

The audit panel reports extraction, prepared-array, CPU memory and synthetic-coordinate checks. No exact duplicate overlap is useful evidence, but it cannot exclude neighbouring patches from the same original scene crossing the split.

## 5. Model performance

The comparison separates the logistic baseline, CNN and CNN + Transformer. Accuracy counts correct answers. Macro F1 gives equal weight to the three classes. Recall measures how many true examples of a class were recognized.

**Example:** the transformer classified 85 of 120 development-validation patches correctly: 70.8%. Health recall improved to 55%, but Rust recall fell from the CNN's 82.5% to 72.5%. Therefore, “better overall accuracy” does not mean “better for every disease class.”

The same validation data selected model checkpoints. These are development results from one seed, not independent field-test scores. Attention combines spatial features derived from PCA; it is not a chemical explanation or direct comparison of original wavelength tokens.

## 6. Inference

1. Select **Check service**. A ready message means the local API responded; it is not an accuracy check.
2. Choose a compatible `.tif` or `.tiff` file.
3. For one original 64 × 64 patch, select **One 64×64 patch → JSON**.
4. Select **Run inference** and read the predicted class and three scores.
5. For a larger compatible raster, select **Tiled raster → ZIP download**, run inference and save the result before leaving the page.

**Example:** an image from `train/Health` can be predicted Rust. That is a possible model mistake, not a change to the folder's reference label. A score of 0.8 would be an uncalibrated class score, not a verified 80% chance of disease. This example is illustrative, not a measured output for that particular file.

Compatible means the same band ordering and sensor scale as the training dataset. RGB images, arbitrary satellite TIFFs and the synthetic 224-band exercise are not compatible simply because they are images. The established extra binary plane in some 126-band source files is checked before removal.

The service accepts at most 128 MiB and 256 tiles, using one local worker. The saved model runs on CPU. One job is processed at a time. Cancel stops the browser request, but already-started server work may finish.

### What is in the downloaded ZIP?

- `predictions.tif`: four bands in order—Health score, Other score, Rust score, class ID (0 Health, 1 Other, 2 Rust).
- `summary.json`: tile positions, classes, scores and processing metadata.

The pipeline reads 64 × 64 windows. Edges are padded by repeating values for model input; output writes are cropped to the original dimensions. A recorded 130 × 97 artificial mosaic required six windows. Each window gets one class-score vector repeated across its pixels; this is not pixel-level segmentation. Coordinates are preserved from the source, not independently certified.

## 7. Map & analytics

The invented farm is divided into 80 cells. With a token, Deck.gl renders them over the Mapbox basemap; otherwise an interactive diagram displays the same cells.

| Control | What it does | Example |
|---|---|---|
| Cell selection | Displays the selected cell and score | Click a cell, or focus a diagram cell and press Enter/Space |
| Minimum score | Includes cells at or above the threshold | At zero all 80 are included; raising it cannot increase the count for a fixed stage |
| Opacity | Changes visual transparency | Lower it to see more of the underlying basemap |
| Heatmap/boundary toggles | Change layer visibility | Hiding the heatmap does not erase the analytics data |
| Timeline | Switches between four invented score stages | Change stage, then inspect the distribution and selected acreage |
| Reset view | Restores the Mapbox camera | Use after panning or rotating the satellite view |

Colours use fixed bins: low below 0.33, medium from 0.33 to below 0.66, and high from 0.66 to 1. The acreage calculation sums the approximate geographic areas of selected cells. The distribution describes the whole grid, even when a threshold hides some cells.

**Example:** a red cell means its simulated score is high under the selected stage. It is not a verified fungal-blight hotspot. The acreage is the area of qualifying demonstration cells, not confirmed crop damage. Four stages do not represent four real acquisition dates or establish a three-week forecast.

Chemical anomalies remain unavailable because Health/Other/Rust are not chemical measurements. “Other” must not be interpreted as nitrogen deficiency or another specific condition.

## 8. Navigation and troubleshooting

Each workspace is a separate page view; Back/Forward and direct hash links are supported. Changing pages resets page-local map controls and upload forms. Leaving Inference cancels the browser request. Download a completed result before leaving.

| Symptom | Action |
|---|---|
| Service unavailable | Start the API on port 8000, then select Check service |
| Another image is being processed | Wait for the current job, then retry |
| Unsupported TIFF | Use a compatible original dataset file; verify selected mode |
| Upload too large | Choose a smaller compatible raster; API limits protect the local machine |
| No satellite tiles | Configure the token and restart Vite, or use the diagram |
| Sample previews unavailable | Check that `frontend/public/explorer` is present; regenerate if needed |
| Different scores from another report | Confirm the model/preprocessing pair and data split; do not mix checkpoints |

## 9. A five-minute project demonstration

1. Overview: explain 900 files and 125 bands.
2. Data quality: select a real sample, inspect one band and explain PCA.
3. Model performance: explain 85/120 correct, macro F1 and the Rust-recall trade-off.
4. Inference: classify a compatible local patch and explain the output scores.
5. Map & analytics: change stage and threshold, select a cell, and state that the farm is simulated.

Conclude accurately: TerraSpectra demonstrates a real-data patch classifier, local tiled inference and simulated GIS analytics. Real farm GPS validation, chemical diagnosis, three-week early forecasting and high-throughput GPU operation still require new evidence and development.
