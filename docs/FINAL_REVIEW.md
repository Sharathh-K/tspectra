# TerraSpectra final review

## The project in one minute

Imagine a leaf image as a book with 125 pages, one page for each measured spectral band. We compress those pages into 16 useful summaries, teach a small neural network to recognize labelled patches, and serve that saved model through a local API. Separately, we build a clearly simulated farm map to demonstrate the interface.

The final review is like checking a school science project before presenting it: check the original materials, repeat the important measurements, show the working demonstration, and clearly say what the experiment cannot prove.

## How this review was approached

1. Re-read the supplied brief and compare every promised feature with the actual data and implementation.
2. Re-read all 900 archive/extracted files, compare SHA-256 fingerprints, and inspect every prepared array.
3. Check saved model, preprocessing and inventory fingerprints against their training reports.
4. Reload both neural networks and recompute their results on the existing 120 development-validation patches. No new training or independent-test claim is made.
5. Recalculate the synthetic grid alignment checks. Keep historical memory/API demonstrations clearly identified as historical evidence.
6. Organize the dashboard into separate views and inspect its navigation and diagram interactions.
7. Package the explanation, evidence, notebook and mentor walkthrough in GitHub.

Reproduce the scientific evidence review from the repository root:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m terraspectra.final_review --zip "/Users/sharath/Downloads/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

Change the archive path on another computer. Week 1 preparation must have created the raw/processed files first. Results go to `reports/final_review/evidence.json`.

## Outcome-by-outcome assessment

| Brief outcome | Delivered evidence | Scope / limitation |
|---|---|---|
| Hyperspectral pipeline | 900 TIFFs, 125 usable bands, 16-component PCA | Real data has 125 bands; the separate 224-band exercise is synthetic |
| 3D CNN | Saved compact 3D–2D CNN and predictions | Patch classification, not chemical stress segmentation |
| Vision transformer | Compact CNN + 16-token attention model | Spatial tokens contain mixed PCA information; no direct wavelength explanation |
| Memory audit | Fresh-process CPU trials, batches 1/8/16/32 | Small-patch CPU evidence, not giant-scene/GPU capacity |
| GIS alignment | 80 synthetic cells checked against Rasterio | Real farm geolocation and live satellite registration unvalidated |
| Inference API | Local FastAPI JSON and ZIP endpoints | CPU, one worker, upload/tile limits; not public deployment |
| Tiling | Window reads and writes, edge padding, four output bands | Patch scores repeated within tiles; not pixel diagnosis |
| Analytics | Model comparison, simulated score distribution and acreage | No measured chemical anomalies or actual disease acreage |
| Timeline | Four labelled invented stages | No observed time series or early-warning forecast |
| Interface | Five separate page views with persistent navigation | Mapbox satellite view requires a token; diagram fallback available |

## Actual model results

All values below use the same 120 development-validation images, 40 per class.

| Model | Correct / 120 | Accuracy | Macro F1 |
|---|---:|---:|---:|
| Logistic regression | 77 | 64.2% | 0.645 |
| Hybrid CNN | 79 | 65.8% | 0.635 |
| CNN + transformer | 85 | 70.8% | 0.707 |

The transformer gained six correct predictions over the CNN on this split. Its class recalls were Health 55%, Other 85%, Rust 72.5%. CNN Rust recall was 82.5%, so aggregate improvement does not mean every class improved. The CNN baseline comparison also shows why accuracy alone is insufficient: logistic regression had higher macro F1 than the CNN despite lower accuracy.

This validation set selected the checkpoints. The results are development evidence, not an independent generalization estimate. There is one seed, no verified scene/plant grouping, and no attention-only ablation. Related source patches may cross partitions even when file hashes are distinct.

## Dashboard pages

- **Overview:** dataset counts and links to the workspaces.
- **Map & analytics:** synthetic heatmap, stages, score filter, acreage and distribution.
- **Inference:** TIFF upload, status messages, patch result or tiled ZIP download.
- **Model performance:** comparison and class recall.
- **Data quality:** preparation summary, integrity, memory and coordinate reports.

These are separate React page views using `#/overview`, `#/map`, `#/inference`, `#/models` and `#/data`, not sections of one long page. Browser Back/Forward and direct hash links select the page. Earlier links such as `#preparation` map to the matching page. The active page is highlighted and the heading receives focus after navigation. No routing dependency was needed.

A page's local state resets when it is unmounted. Returning to the map starts the default stage/filter; leaving Inference cancels the browser request and clears the form, though already-started server work may finish. This behavior is deliberate and documented; there is no promise of persistent uploads or saved map selections.

No week numbers or review-stage labels are used in dashboard navigation. Historical filenames and instructional documents retain them for traceability.

## Evidence files

- `reports/final_review/evidence.json`: fresh integrity, model and geometry checks.
- `reports/final_review/dashboard-overview.png`: overview screenshot.
- `reports/week3/metrics.json`: full training metadata and per-class metrics.
- `reports/week4/api_demo.json`: earlier successful local API requests.
- `reports/week4/tiling_demo.json`: earlier six-window artificial mosaic example.
- `notebooks/06_final_review.ipynb`: simple explanations and visual evidence summary.

## Review conclusion

TerraSpectra is a completed educational prototype for compatible hyperspectral patch classification, a local tiled-inference service, and a simulated geospatial dashboard. The original brief's field-scale disease forecasting, chemical identification and GPU throughput aspirations are not fulfilled by this dataset and evidence. Present that distinction clearly rather than claiming a production agriculture system.

The next scientific steps would be source-grouped independent evaluation, more labelled scenes and sensors, measured chemical targets, trustworthy georeferencing, and repeated time-stamped acquisitions. Each requires new evidence; changing the interface wording cannot supply it.
