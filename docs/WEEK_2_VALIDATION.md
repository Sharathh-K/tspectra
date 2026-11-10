# Week 2 validation — 11 November 2026

## Completed computation

- Rechecked all 900 extracted files against the supplied ZIP sizes and CRCs; all matched.
- Reused the inspected Week 1 inventory and the 900 prepared arrays from the supplied
  ZIP. This preserves the original training/development split and class mapping.
- Trained the compact hybrid CNN on all 480 training images and evaluated on all
  120 labelled development-validation images each epoch.
- Bounded run stopped after 16 epochs with the checkpoint from epoch 11.
- Measured 55.15 seconds after imports for loading/training/evaluation/export;
  plotting is outside that timer. Peak process RSS before plotting: 313.05 MiB.
- Input tensor per batch: 0.25 MiB. Cached 600 labelled inputs: 9.375 MiB.
  These tensor sizes exclude activations, gradients and library overhead; use the
  process measurement for the broader memory picture.
- Saved probabilities and predicted classes for 120 validation and 300 unlabelled
  images. No accuracy is claimed for the unlabelled set.
- Saved tensor weights and numeric preprocessing parameters; no retraining needed
  to use the supplied pair for raw-TIFF inference.

## Results

| Model | Accuracy | Macro F1 |
| --- | --- | --- |
| Constant-class baseline | 33.33% | — |
| Logistic regression | 64.17% | 0.6446 |
| Hybrid CNN | 65.83% | 0.6346 |

These scores do not establish significance or new-farm generalization. The CNN's
Health recall is 30%; 20 of 40 Health patches are predicted Rust. The model needs
improvement, and the baseline has higher macro F1. The same validation set selects
the checkpoint. There is no separate independent test result.

## Automated checks

- Four Python checks passed: correct pooling/component axes, valid forward/backward
  gradients, raw-TIFF preprocessing matching Week 1 for both 125/126-band files,
  and reloaded-model predictions matching saved development metrics and CSV values.
- Four frontend checks passed: 80 aligned/closed polygon cells, fixed colour-bin
  boundaries, rejection of malformed responses and correct threshold extremes.
- Strict TypeScript checking passed.
- Vite production build passed. The map libraries still produce a large-bundle
  warning (about 2.56 MB minified JavaScript); this is not a compilation failure.
- The 25-cell Week 2 notebook executed successfully and includes three embedded figures. Opening it does not
  automatically train again: `RUN_TRAINING` is False.

## Interactive verification limits

The local preview successfully served the mock JSON response.
The browser automation connection timed out before a page could be inspected.
The source and data-contract checks above are complete, but actual browser pointer
interactions, keyboard selection, mobile layout and live WebGL/map alignment remain
manual checks. No Mapbox token was supplied, so live satellite imagery cannot be
claimed as verified. A labelled SVG diagram is available without a token.

Manual steps: start the frontend, confirm 80 cells at threshold zero, select a cell,
change opacity, hide/show the heatmap and boundary, move the threshold to one (zero
cells), restore zero, and use keyboard selection. With a public token, also pan,
zoom, rotate, tilt and reset the map; the overlay should remain aligned.

## Scope achieved and scope deferred

Week 2 supplies a trained **patch classifier** and a **simulated grid overlay**.
The requested chemical-stress pixel labels are absent from the ZIP, so they are not
invented. Transformer integration is Week 3. FastAPI and large-image tiling are
Week 4. The model's predictions are never attached to invented farm coordinates.
