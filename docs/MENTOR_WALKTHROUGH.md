# Five-minute mentor walkthrough

## 0:00 — Explain the problem and data

“TerraSpectra explores hyperspectral crop-image classification. Our supplied dataset contains 900 patches, including 600 Health/Other/Rust labels. It has 125 usable bands. We use 480 images for training, 120 for development validation, and leave 300 unlabelled images for prediction only.”

## 0:45 — Show Data quality

“Think of each patch as a stack of transparent pages. Training-only scaling and PCA compress them to 16 components. We checked archive integrity, memory use, and numerical alignment of our invented map grid.”

## 1:30 — Show Model performance

“The CNN looks for local patterns. The small transformer lets image-region summaries compare information. The hybrid reached 70.8% development accuracy and 0.707 macro F1. This set also selected the checkpoint, so these are not independent test results.”

If asked whether the transformer is always better: explain that Rust recall fell from 82.5% to 72.5%, despite better overall metrics. One run does not establish statistical significance or isolate attention's contribution.

## 2:15 — Show Inference

Start the local API using the README. Select a real 64×64 TIFF from the prepared dataset and run patch prediction. Explain that the three numbers are uncalibrated class scores. For tiling, show the saved artificial mosaic demonstration and its six windows. Output blocks are patch predictions repeated spatially, not a learned pixel disease mask.

## 3:15 — Show Map & analytics

Move the simulated timeline and minimum-score sliders. Explain that area changes because the selected invented cells change. No real observation dates or geographic association with the uploaded patches are available. The no-token diagram demonstrates the UI; it does not verify satellite registration.

## 4:15 — Close with honest limits

“The software demonstrates the data pipeline, two model architectures, an API, tiling and geospatial interaction. Real-farm disease forecasts, chemical diagnosis and GPU-throughput claims need additional data and evaluation.”

## Likely questions

**Why not predict three weeks ahead?** There are no verified dated sequences and future-outbreak targets.

**Why does the map not show the uploaded prediction?** Its farm coordinates are invented and unrelated to the dataset's uncertain georeferencing.

**Why not identify chemicals from Other?** Other is a class label, not a measured deficiency or concentration.

**Why does a border tile look blocky?** The model predicts whole patches; partial edges are padded and output writes are cropped.

**Can I reproduce it?** Yes: commands, saved weights, reports, notebook outputs and environment requirements are in the repository. The dataset remains local and must be obtained separately under its terms.
