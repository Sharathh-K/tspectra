# Week 2 — Hybrid CNN and heatmap rendering

## Objective

The second milestone was to train a compact hyperspectral classifier and build a coloured grid overlay. The actual labels supported Health, Other and Rust patch classification, so the implementation used those categories rather than inventing chemical-stress labels.

## Work completed

I reused the Week 1 preprocessing and 480/120 split. Each 64 × 64 × 16 PCA array was spatially averaged to 16 × 16 × 16 to reduce computation. The PyTorch network uses two 3D convolution layers, followed by a 2D convolution and a classification head. This combines local information across PCA components and image locations.

Training used cross-entropy loss and Adam, with a maximum of 20 epochs and early stopping. The completed run stopped after 16 epochs and retained the checkpoint from epoch 11. I also trained a logistic-regression baseline so that the neural network could be compared with a simpler method. Model weights, preprocessing parameters, training history and predictions were saved for reuse.

For the dashboard, I implemented an 80-cell grid from explicitly mock JSON. Deck.gl displays its polygons using consistent score colours. Controls allow users to select cells, change opacity, filter scores, and toggle the heatmap or farm boundary. An interactive diagram makes the demonstration usable without satellite tiles.

## Simple explanation

The CNN moves small windows through a stack of image pages and learns useful patterns. It gives one answer for the whole patch. The heatmap is a separate practice exercise: colour squares on an imaginary farm using invented scores.

## Recorded results

| Model | Development accuracy | Macro F1 |
|---|---:|---:|
| Logistic regression | 64.17% | 0.6446 |
| Hybrid CNN | 65.83% | 0.6346 |

The recorded CPU run took about 55 seconds for loading, training, evaluation and export, excluding imports and plotting. Health recall was only 30%, revealing a weakness that overall accuracy alone would hide. The baseline's higher macro F1 also showed that the CNN was not uniformly better.

## Review following this milestone

The subsequent mid-project audit checked all 900 extracted files and prepared arrays. It recorded small CPU training-memory trials at batch sizes 1, 8, 16 and 32, and checked the geometry of all 80 synthetic map cells. These were additional audit activities, not proof of giant satellite-cube capacity or actual farm registration.

## Limitations and next step

The classifier predicts patch categories, not infected pixels or chemical deficiencies. Mock map scores are independent of model predictions. Validation also selected the checkpoint, so these are development results rather than independent test results. The next milestone introduced attention and analytics.

## Supporting material

- [Model and heatmap guide](../WEEK_2_GUIDE.md)
- [Recorded results and checks](../WEEK_2_VALIDATION.md)
- [Teaching notebook](../../notebooks/02_week_two_model_and_heatmap.ipynb)
- [Subsequent audit results](../MID_PROJECT_RESULTS.md)
