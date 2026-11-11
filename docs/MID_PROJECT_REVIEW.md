# Mid-project review: checking our work before adding more

## The idea, explained simply

Imagine moving a library into a new classroom. First we check that every book arrived unchanged. Then we see how many books fit on a desk. Finally, we check that the classroom map puts every desk in the right square.

Our project does the same three jobs:

1. **Extraction audit:** Did all the image files arrive safely, and are their prepared arrays usable?
2. **Memory audit:** Can the computer run real forward, backward, and optimizer steps with different batch sizes?
3. **GIS validation:** Do our demonstration map cells fill the correct rectangle, with the correct coordinates?

This review is a checkpoint, not a new prediction model. It keeps the Week 2 model unchanged. Transformer work belongs to Week 3.

## What the provided data can support

The archive has 900 TIFF patches. There are 600 labelled examples (Health, Other, Rust) and 300 unlabelled examples. Week 1 splits the labelled examples into 480 training and 120 development-validation patches. Images have 125 usable spectral bands; some have an extra band handled by the existing loader. PCA creates 16 components, which are mathematical combinations of bands, not 16 physical wavelengths.

The screenshot describes a much larger satellite system. This dataset does not establish chemical deficiency labels, pixel-level disease labels, surveyed farm coordinates, or three-week forecasting targets. TIFF metadata exists, but an unknown/nonstandard CRS is not enough to locate these patches reliably. We do not assign the invented Bengaluru farm coordinates to those images.

## 1. Extraction audit: check every book

Run from the repository root in the VS Code terminal:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m terraspectra.review --zip "/Users/sharath/Downloads/beyond-visible-spectrum-ai-for-agriculture-P1.zip"
```

On another computer, replace the ZIP path. Prepare the Week 1 data first if `data/raw`, `data/processed`, or `reports/inventory.csv` is missing. See the README.

For every TIFF, the audit:

- Reads the ZIP member in small chunks without extracting another dataset copy.
- Calculates its SHA-256 fingerprint and compares it with the extracted file and Week 1 manifest.
- Checks the prepared array is finite float32 with shape `(64, 64, 16)`.
- Counts raw bands, splits, and recognized EPSG identifiers.
- Checks whether identical file fingerprints occur across splits.

A fingerprint is like a book's unique checksum. Equal fingerprints strongly support byte-for-byte identity. Different neighbouring image patches can still be correlated: zero exact duplicates does **not** prove the validation split is independent by plant or original scene.

The audit stops with an error if an integrity or shape check fails. Previously generated reports are snapshots; a failed run does not certify them for changed inputs.

## 2. Memory audit: how many books fit on the desk?

A batch is a group of examples processed together. We try batch sizes **1, 8, 16, and 32**, each in a new Python process. Each process loads the actual 480 training inputs and performs three complete training steps with a temporary model. The saved Week 2 checkpoint is never overwritten.

For each step:

1. Read a group of examples.
2. Make class predictions.
3. Calculate the prediction error (loss).
4. Calculate gradients: which weights should move and in which direction?
5. Update weights using Adam.
6. Check that the loss and gradients are finite numbers.

The input shape is `(batch, 1, 16, 16, 16)`: examples, channels, PCA depth, height, width. Four bytes store one float32 number. A batch of 16 therefore uses `16 × 1 × 16 × 16 × 16 × 4` bytes, or **0.25 MiB**, for inputs alone.

The process uses more memory than that. It also holds Python, PyTorch, cached inputs, model weights, intermediate activations, gradients, and Adam state. **Peak process RSS** measures the largest resident-memory footprint observed by the operating system during that process. It is not the same as tensor bytes or GPU memory. It includes startup and dataset loading. Runtime includes loading and the three steps, excluding interpreter/import startup.

The pooled training cache is 7.5 MiB. The implementation briefly holds both individual inputs and their stacked copy during construction; peak RSS captures this too. The existing dataset loads one PCA cube at a time and caches small pooled inputs. It does not load every original hyperspectral cube into RAM.

Fresh-process RSS can vary with operating-system memory residency and library allocation, so a larger batch can occasionally show a lower observed peak. These are single short measurements, not a monotonic scaling curve or proof of a maximum safe batch size.

Keep batch size 16 as the existing practical default. These short trials establish bounded CPU feasibility for this small model. They do not establish capacity for full-resolution satellite cubes, all GPU devices, or long-duration training. Earlier Week 2 training provides a longer run, but it is still a small-patch experiment.

## 3. GIS validation: checking the map squares

GeoJSON uses **longitude first, latitude second**. Our invented farm is a rectangle, and the mock heatmap contains 80 cells (10 columns × 8 rows).

The dashboard and Python audit now read the same `frontend/src/demo-farm.json` boundary. The audit independently builds a Rasterio affine transform from the grid bounds and checks:

- The displayed farm rectangle exactly matches the mock grid bounds.
- Every grid position is present exactly once, with unique cell IDs.
- Every cell's corners agree with Rasterio's calculated corners within `1e-9` degrees.
- A cell center converts from row/column to coordinates and back to the same row/column.

**The tricky part:** mock JSON row zero starts at the south edge; raster row zero starts at the north edge. We use `raster_row = rows - 1 - mock_row`. Without that flip, the map would appear upside down.

Because each unique cell matches its expected rectangle and every position is present, the cells cover this rectangular farm without gaps or overlap beyond numerical tolerance. This does not generalize to arbitrary irregular farm boundaries without additional clipping/geometry checks.

### What still requires real-world evidence

Three separate claims must stay separate:

| Claim | Review result |
|---|---|
| Synthetic cell coordinates and boundary agree | Automatically checked |
| Live map stays aligned while zooming, rotating and tilting | Manual browser check still required |
| Dataset patches align with an actual surveyed farm | Cannot be validated from current resources |

Deck.gl's `MapboxOverlay` shares camera control with Mapbox, which is the correct integration approach. That architecture alone does not prove that this exact dashboard renders correctly on every device.

For manual browser validation, provide a Mapbox public token as described in the README. Open the heatmap, inspect all four farm corners, pan, zoom, rotate and tilt; toggle the boundary and grid; check that the outside grid edges remain on the boundary. Record browser, date, screenshots and pass/fail observations. A no-token SVG preview only checks a diagram; it cannot certify Mapbox rendering.

For real-farm validation, obtain a trusted source CRS, georeferenced image transform, surveyed boundary/control points and acquisition metadata. Transform into the map CRS and measure position errors against those reference points before claiming alignment.

## Files to present to your mentor

- `reports/mid_review/audit.json`: measured results and machine details.
- `notebooks/03_mid_project_review.ipynb`: beginner-friendly walkthrough and charts.
- `docs/MID_PROJECT_RESEARCH.md`: primary sources and decisions.
- Dashboard → **Mid-project review**: short summary of the same report.

The raw dataset stays local and ignored by Git. The report, source, notebook and small frontend JSON are committed. Re-run the audit after changing input data, pooling, model architecture or map geometry.
