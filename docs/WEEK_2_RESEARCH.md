# Week 2 research and design decisions

Research checked 11 November 2026. The supplied screenshots define the weekly scope;
the actual local ZIP determines which labels and measurements we can use.

## What the screenshots ask for, and what the data permits

Week 2 asks for a hybrid 3D CNN in PyTorch and a coloured map grid driven by mock
JSON. Week 3 introduces a transformer, so we keep attention out of this week's model.
The plan's phrase “healthy versus chemically stressed pixels” cannot be implemented
as a verified supervised task with this ZIP. It supplies Health, Other and Rust
**patch labels**, not chemical measurements or pixel masks. We train those three
classes. Turning patch labels into thousands of claimed pixel labels would overstate
the available ground truth.

The downloaded archive has 900 TIFFs, including 600 labelled examples and 300
unlabelled competition validation files. We retain the Week 1 development split.
Its limitations remain: source scene/date grouping is unavailable, and patches may
share their original scene. These are not independent farm-level test scores.

## Sources and the decisions they informed

| Primary source | What it establishes | Decision in this project |
| --- | --- | --- |
| [Roy et al., HybridSN paper](https://arxiv.org/abs/1902.06701) and [authors' code](https://github.com/gokriznastic/HybridSN) | Combines a 3D spectral–spatial feature extractor with a 2D spatial stage | Use the same architectural idea in a much smaller original PyTorch implementation; do not copy paper accuracy or claim an exact reproduction |
| [Zhang et al., wheat yellow-rust study](https://www.mdpi.com/2072-4292/11/13/1554) | Investigates UAV hyperspectral disease classification using spatial and spectral information | Keep disease classification as the task; the paper's acquisition schedule does not create date labels or geographic ground truth in our ZIP |
| [PyTorch 2.8 Conv3d](https://docs.pytorch.org/docs/2.8/generated/torch.nn.Conv3d.html) | Specifies the N,C,D,H,W input convention | Explicitly convert to batch × 1 × 16 components × 16 height × 16 width |
| [PyTorch 2.8 CrossEntropyLoss](https://docs.pytorch.org/docs/2.8/generated/torch.nn.CrossEntropyLoss.html) | Accepts logits and integer class targets | Return three raw scores during training; apply softmax only to display inference scores |
| [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | Explains leakage when preprocessing learns from evaluation data | Reuse training-only Week 1 scaling/PCA; baseline's scaler also fits training only |
| [Deck.gl GeoJsonLayer](https://deck.gl/docs/api-reference/layers/geojson-layer) | Supports coloured polygons, picking and GeoJSON geometries | Render one polygon per simulated cell with fixed colour bins |
| [Deck.gl HeatmapLayer](https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer) | Uses kernel density estimation to smooth point weights | Do not smooth the requested cell grid into blobs; colour individual cells so each value remains inspectable |
| [Deck.gl MapboxOverlay](https://deck.gl/docs/api-reference/mapbox/mapbox-overlay) | Synchronizes Deck.gl rendering with the Mapbox camera | Retain one map camera for panning, rotation and pitch |

## Why this small architecture

The Week 1 PCA arrays have 16 components. Each component is a mixture of wavelengths,
ordered by explained variance. Adjacent PCA components are **not adjacent physical
wavelengths**. A 3D CNN here learns local component-and-image patterns, not guaranteed
physical wavelength continuity. This is a computational compromise inspired by PCA
plus hybrid CNN workflows, and should be compared against full-band approaches later.

We average non-overlapping 4×4 image blocks to reduce 64×64 to 16×16 while preserving
the whole patch's field of view. This cuts spatial computation by 16; it may lose
fine lesions or textures. It is chosen for the user's small laptop and short training
budget, not asserted to be the best representation for every disease.

The network has two small 3D convolutions, one 2D convolution, global average pooling,
dropout and a three-class linear head. It contains 23,703 trainable parameters.
A single seeded run uses Adam, learning rate 0.001, weight decay 0.0001, batch size
16, at most 20 epochs and early stopping after five unimproved validation losses.
CPU uses two threads and zero data-loader worker processes. No large pretrained
model, transformer, hyperparameter search or separate GPU library is needed.

## Why a baseline is essential

A logistic regression model uses the per-component mean and standard deviation of
the same pooled training inputs. Its 32-number representation is a useful check:
does our extra neural-network work improve anything? Both models use the identical
480/120 split. Report accuracy, macro F1, per-class precision/recall and a confusion
matrix. A balanced split's constant-class accuracy is 33.3%.

In the recorded run the CNN accuracy is 65.8% versus 64.2% for the baseline, but
the baseline macro F1 is higher (0.645 versus 0.635). The difference is small and
does not establish a statistically significant improvement. CNN Health recall is
only 30%; 20 of 40 Health patches are predicted Rust. This is an experimental
learning model, not a treatment decision system. No further architecture search was
performed to improve this validation result.

The same development set selects the best checkpoint and reports performance.
There is no independent labelled test set in this delivery. The 300 unlabelled
files receive predictions only. Future work needs independent scene/farm splits,
more labelled data and probability calibration before field claims.

## Why the map is a separate simulation

The plan explicitly allows mock backend JSON in Week 2. We generate 80 cells inside
the existing invented boundary, with two artificial score peaks. `is_mock: true`
and a source note travel with the data. Scores are invented display values, not
calibrated infection probabilities. None of the 300 unlabelled image predictions is
assigned to those coordinates. The actual model report appears in its own panel.

The same JSON drives an SVG diagram without a token and Deck.gl polygons over a
Mapbox satellite basemap with a token. Both use green <0.33, amber 0.33–<0.66, and red
≥0.66. Opacity changes visibility; filtering hides cells below a chosen score.
Neither control retrains the model or changes the data. A future API can return
this documented contract once appropriately georeferenced inputs exist.
