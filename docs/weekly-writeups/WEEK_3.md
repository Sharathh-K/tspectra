# Week 3 — Vision Transformer and analytics

## Objective

The third milestone explored whether attention could improve the compact classifier and added understandable analytics to the dashboard.

## Work completed

I built a compact CNN + Vision Transformer using the same training split, three labels and train-fitted preprocessing. After the 3D convolution layers, a projection converts the learned spatial features into 16 tokens, each containing 32 numbers. Learned position embeddings preserve their locations. One transformer encoder layer with four attention heads allows the tokens to exchange information before the final classification step.

The model was trained from scratch, rather than downloading a large pretrained network or fine-tuning the Week 2 checkpoint. It contains 24,407 parameters. Training used seed 42, batches of 16, Adam, and early stopping based on validation loss. The best checkpoint, training history, confusion matrix and predictions were saved.

The analytics panel uses the same 80 simulated cells as the map. It displays the number of cells above the selected threshold, their approximate combined acreage and the distribution of low, medium and high scores. Geographic rectangle area is calculated using a spherical Earth approximation. A separate model comparison presents measured classification results. The panel explains that chemical-anomaly labels are unavailable.

## Simple explanation

The CNN writes a short note about each part of the image. The transformer lets those notes compare information before choosing a class. The analytics panel adds up the areas of selected squares on the demonstration farm.

## Recorded results

| Model | Development accuracy | Macro F1 |
|---|---:|---:|
| Week 2 CNN | 65.83% | 0.6346 |
| CNN + Transformer | 70.83% | 0.7066 |

The transformer correctly classified 85 of 120 validation patches, six more than the CNN. Health recall increased from 30% to 55%, while Rust recall decreased from 82.5% to 72.5%; Other recall remained 85%. The recorded CPU run took approximately 19.1 seconds with peak process memory of 351.9 MiB. These historical runtimes are not a controlled speed comparison.

## Limitations and learning

Attention operates on spatial tokens containing mixed CNN/PCA features, not directly on the original wavelength bands. This experiment does not demonstrate chemical explanations or establish that attention alone caused the improvement. It used one seed and the validation set also selected the checkpoint. The acreage values describe a simulated farm, not measured disease risk.

The next milestone was to expose the saved model through an API and process compatible images in tiles.

## Supporting material

- [Transformer and analytics guide](../WEEK_3_GUIDE.md)
- [Measured results](../WEEK_3_RESULTS.md)
- [Teaching notebook](../../notebooks/04_week_three_transformer.ipynb)
- [Research notes](../WEEK_3_RESEARCH.md)
