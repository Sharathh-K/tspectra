# Week 3: a small transformer and understandable analytics

## First, the plan in everyday language

Imagine four children looking at different parts of the same leaf picture. Each child writes a small note about what they see. Then they compare notes before deciding whether the picture belongs to Health, Other or Rust.

The CNN writes the notes. The transformer lets the notes talk to each other. The classifier makes one decision for the whole image patch. This is a compact CNN + vision-transformer experiment, not a reproduction of a large pretrained ViT.

For the dashboard, imagine putting a transparent grid over an invented farm. We add up the area of squares whose invented score is above your selected threshold. That demonstrates the analytics interface without pretending we know where the Kaggle patches were collected.

## What stays the same

We use the same 480 training patches and 120 development-validation patches as Week 2, the same train-fitted scaling/PCA, and the same three classes. The 300 unlabelled patches receive predictions but cannot provide accuracy measurements. The mid-project audit already compared all 900 extracted TIFFs with the supplied ZIP and checked the prepared arrays. The manifest fingerprint is recorded again with the model results.

The raw dataset has 125 usable bands, not the 200+ bands imagined in the project brief. PCA makes 16 mixed components. It does not preserve a simple one-component-to-one-wavelength correspondence.

## Model: follow the shapes

`N` means the number of examples in one batch.

| Step | Shape | Simple explanation |
|---|---|---|
| Existing pooled input | N × 1 × 16 × 16 × 16 | A small stack of PCA pages |
| Two 3D convolutions | N × 12 × 8 × 8 × 8 | Learn local depth and image patterns |
| Fold depth into channels | N × 96 × 8 × 8 | Keep depth features in each location |
| 2×2 token projection | N × 32 × 4 × 4 | Turn groups of features into short notes |
| Flatten spatial grid | N × 16 × 32 | Sixteen notes, each with 32 numbers |
| Add position + attention | N × 16 × 32 | Remember note locations and compare notes |
| Average + classifier | N × 3 | Make three class scores |

One transformer encoder layer has four attention heads and a 64-unit feedforward layer. Position embeddings are learned. Mean pooling combines the output tokens; there is no special class token. Training starts from random weights, including the CNN. It does not fine-tune Week 2 weights or download a large pretrained model.

**What attention actually compares:** spatial tokens enriched by CNN features from PCA depth. It is not explicit attention between 125 original wavelength bands. Calling its scores chemical measurements or wavelength explanations would be incorrect. CNN processing combines local depth information; attention exchanges that learned information between image regions.

## Training: one small, fixed experiment

- CPU, two threads, batch size 16, seed 42.
- Adam, learning rate 0.001, weight decay 0.0001.
- At most 20 epochs; stop after five epochs without meaningful validation-loss improvement.
- Save the checkpoint with the lowest validation cross-entropy, then reload it for reported results.
- Same baseline calculation and data split as Week 2.

Run from the repository root:

```bash
source .venv/bin/activate
PYTHONPATH=src python -m terraspectra.train --architecture hybrid_vit
```

The default command without `--architecture` still trains Week 2. Week 3 writes to `models/week3`, `reports/week3`, and `frontend/public/week3-summary.json`. It does not overwrite Week 2 results.

Predict a real TIFF using the new saved model:

```bash
PYTHONPATH=src python -m terraspectra.predict "data/raw/train/Health/hyper (1).tif" --model-dir models/week3
```

Scores are uncalibrated patch-class scores. They do not locate infected pixels.

## Analytics: what the numbers mean

The panel reads the same validated 80-cell JSON used by the map. Moving the minimum-score slider updates selected cell count and approximate acreage. Hiding the map layer affects visibility only; it does not erase the selected data. The distribution chart always describes the whole grid, using the same low/medium/high boundaries as the map colors.

For a longitude/latitude rectangle, we approximate the Earth as a sphere:

`area = radius² × longitude_width_in_radians × (sin(north) − sin(south))`

We divide square metres by 4046.8564224 to obtain acres. This follows from integrating the spherical surface element over the rectangle. The radius is 6,371,008.8 metres. It is an approximate display calculation for this synthetic rectangle, not a survey-grade measurement or arbitrary polygon-area algorithm. The invented boundary is not assumed to be 1,000 acres just because the screenshot gives that example.

“Flagged area” means invented cells above an invented score threshold. It is not an estimate of actual disease acreage. The real classification comparison appears in a separate section and does not feed these mock scores.

### Why chemical anomalies are unavailable

The classes are Health, Other and Rust. There are no verified labels for nitrogen deficiency, chlorophyll concentration, fungal chemicals or other specific compounds. The panel explicitly explains this. “Other” must not be renamed “chemical stress.” Collect corresponding chemical measurements and a suitable validated task before implementing chemical diagnosis.

## How to read the comparison

Accuracy counts correct predictions. Macro F1 gives each of the three classes equal importance. Recall asks how many actual examples of a class were found. Read all three rather than choosing only the nicest number.

This run changes the architecture and adds attention. It is not a controlled attention-only ablation. A single seed and a development set used for checkpoint selection cannot establish statistical significance or performance on unseen farms. Neighbouring-source-patch leakage remains possible. Better scores here are encouraging experimental evidence only.

Open `notebooks/04_week_three_transformer.ipynb` in VS Code, select `.venv`, and run the cells. It loads the small saved report/model by default; optional retraining is off. For the dashboard, follow the existing frontend setup in the README, refresh and open **Week 3 transformer** or **Analytics**. The diagram works without a Mapbox token; satellite rendering still requires one.

## What to present

1. Explain the model shape table and “notes talking to notes” analogy.
2. Show the saved real metrics and confusion matrix.
3. Move the map threshold slider and explain the simulated acreage calculation.
4. State the unsupported outcomes: chemical diagnosis, real farm disease mapping and three-week forecasting.
5. Use `docs/WEEK_3_RESEARCH.md` to explain the design choices.
