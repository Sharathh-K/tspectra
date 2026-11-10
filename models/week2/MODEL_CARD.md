# TerraSpectra Week 2 model

**Purpose:** a small internship prototype for classifying hyperspectral wheat image
patches into Health, Other and Rust. This is not a pixel segmentation or forecasting
model. It is a compact original implementation inspired by the
[HybridSN architecture](https://arxiv.org/abs/1902.06701).

## Files and interface

- `hybrid_cnn.pt`: saved tensor weights and simple metadata, loaded with
  `torch.load(..., weights_only=True)`. About 100 KB.
- `preprocessing.npz`: numeric scaler/PCA parameters from Week 1, loaded with
  `allow_pickle=False`. Use this exact recipe with these weights.
- Input to `predict.py`: a 64×64 TIFF patch with 125 useful bands, optionally the
  verified binary 126th plane described in Week 1.
- Input to the neural network: batch × 1 × 16 PCA components × 16 × 16 pixels.
- Output order: Health=0, Other=1, Rust=2. Softmax values are uncalibrated scores.

Do not combine these weights with a newly fitted PCA just because it has the same
number of components. Raw-TIFF prediction uses the bundled recipe; retraining the
model exports a matching replacement pair.

## Training

Source: the user's Beyond Visible Spectrum: AI for Agriculture 2023 ZIP.
600 labelled patches split 480/120 with seed 42, stratified by class. The additional
300 unlabelled patches were used for inference only. Scaling/PCA were fitted on a
sample of training pixels in Week 1. A 4×4 average pool reduces the spatial grid.

PyTorch 2.8.0, CPU, two threads, seed 42, 23,703 parameters, batch 16, Adam at 0.001,
weight decay 0.0001, dropout 0.2. Maximum 20 epochs, early stopping patience 5.
Recorded run ended after 16 epochs; lowest validation-loss weights came from epoch 11.
No separate hyperparameter search or independent final test was performed.

## Development results

Accuracy 65.83%; macro F1 0.6346. Logistic baseline accuracy 64.17%, macro F1 0.6446.
The CNN is not a consistent improvement across measures. CNN Health recall is 30%,
Other recall 85%, Rust recall 82.5%. There are only 40 examples of each class in the
validation set. Inspect `reports/week2/validation_predictions.csv` and the confusion
matrix in `reports/week2/metrics.json` to see the mistakes.

Training/evaluation runtime measured after imports: 55.15 seconds; peak process
memory measured before plotting: 313.05 MiB. Runtime and memory vary by platform.

## Limitations

- Validation also selects the best epoch, so these are development scores.
- No verified source-scene/farm/date groups; neighbouring patches may be correlated.
- Only patch labels; no confirmed pixel masks, chemical stress or timing labels.
- Averaging spatial blocks can remove small features; PCA loses physical band order.
- Model probability calibration, field generalization and satellite transfer untested.
- No claim of identifying disease three weeks before symptoms.
- Frontend geographic heatmap is independent simulated data, not these predictions.

Dataset terms remain those of the [Kaggle competition](https://www.kaggle.com/competitions/beyond-visible-spectrum-ai-for-agriculture-P1/rules).
No raw training images are included in this directory. Model/recipe fingerprints are
recorded in `reports/week2/metrics.json`.
