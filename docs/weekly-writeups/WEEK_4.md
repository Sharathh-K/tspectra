# Week 4 — Inference API, tiling and interface polish

## Objective

The fourth milestone made the saved model accessible through a local API, added window-based inference, and introduced a timeline demonstration in the dashboard.

## Work completed

I implemented a FastAPI service that loads the saved Week 3 transformer and preprocessing recipe. Its endpoints provide service health, predictions for a compatible TIFF patch, and a downloadable ZIP containing tiled predictions and a summary. The dashboard includes upload controls, loading and error messages, results and download actions.

The tiling pipeline reads compatible rasters in 64 × 64 windows. For incomplete edge windows, it repeats edge values to create a full model input, then crops the output back to the original extent. The output TIFF contains four bands: Health, Other and Rust scores, plus the predicted class ID. Each patch's result is repeated across its window. The source dimensions, transform and CRS are preserved.

I added four explicitly simulated timeline stages. Selecting a stage updates the same map and analytics data so their displays remain consistent. Real uploaded-image predictions remain separate from this invented farm history. Beginner-friendly documentation and a notebook explain the complete flow.

## Simple explanation

The API is a reception desk: it accepts an image, sends it to the saved model and returns an answer. Tiling is like cutting a large sheet into manageable squares, processing each square, and putting the answers back in their original positions.

## Recorded demonstrations

A real dataset patch and an artificial 130 × 97 pixel mosaic both returned successful HTTP 200 responses from the local API. The mosaic required six windows and produced a four-band output with dimensions 97 × 130. Its recorded small tiling run took approximately 0.25 seconds including model loading; this is a demonstration, not a throughput benchmark.

The 19-cell notebook executed successfully. The delivery record also reports successful TypeScript checking and frontend production compilation, with an existing large-bundle warning.

## Subsequent final-review polish

After the Week 4 implementation, dashboard milestone labels were replaced with feature names. The final review organized the interface into five separate views: Overview, Map & analytics, Inference, Model performance and Data quality. It rechecked file integrity and reproduced saved model metrics. These later refinements are distinguished from the original Week 4 delivery.

## Limitations and conclusion

The API is a local CPU implementation with a 128 MiB upload limit and 256-tile API limit. GPU throughput and giant-scene memory performance were not demonstrated. Tiled outputs are repeated patch scores, not pixel-level segmentation. Preserving coordinates does not establish that they are correct. The timeline is simulated, and no real three-week forecast or chemical diagnosis is claimed.

Together, the four milestones deliver a hyperspectral classification prototype, a local tiled-inference service and a simulated geographic dashboard.

## Supporting material

- [API and tiling guide](../WEEK_4_GUIDE.md)
- [Delivery record](../WEEK_4_RESULTS.md)
- [Teaching notebook](../../notebooks/05_week_four_api_and_tiling.ipynb)
- [Subsequent final review](../FINAL_REVIEW.md)
