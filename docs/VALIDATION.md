# Week 1 validation record

Checked on 11 November 2026 against the ZIP provided by the user.

## Actual data preparation

- Extracted all 900 TIFF files; original archive left intact.
- Read every file with Rasterio. All patches are 64 × 64 pixels.
- Counted 741 files with 125 bands and 159 with an extra binary plane.
- Inspected every extra plane: 154 constant 65,535, three constant zero,
  two containing both zero and 65,535. No other values were found in those planes.
- Kept the first 125 bands; recorded original band counts and removal flags.
- Created the seed-42 stratified split: 160 train and 40 validation per labelled
  class; 300 original competition validation images kept unlabelled.
- Checked file fingerprints for exact duplicates crossing partitions; none blocked
  preparation. This does not establish independence of neighbouring image patches.
- Fitted StandardScaler and PCA using 30,720 sampled training pixels only.
- Retained 16 components, with sampled retained variance 0.9992254 (99.92%).
- Wrote 900 float32 NumPy arrays, each 64 × 64 × 16; checked every array for expected
  shape, type and finite numbers. Total saved array bytes: 236,044,800.
- Confirmed the frontend summary equals the generated preparation report.
- Executed all notebook code cells successfully, including a comparison of the
  notebook transformation with the saved processed array and the synthetic exercise.

## Frontend

- Installed dependencies and included the pnpm dependency lockfile.
- TypeScript strict checking passed.
- Vite production build passed. The map libraries create a large JavaScript bundle
  (about 2.55 MB before compression); Vite reports a size warning, not a build error.
- Local preview returned HTTP 200.
- Browser automation was unavailable because its tab-opening operation timed out.
- No Mapbox token was supplied. Satellite tiles, map movement, WebGL rendering and
  actual polygon alignment still require the manual steps in the Week 1 guide.
  The source includes explicit missing-token and map-error states.

## Reproducibility environment

Python 3.9; NumPy 2.0.2; Rasterio 1.4.3; scikit-learn 1.6.1;
Matplotlib 3.9.4; joblib 1.5.3; nbclient 0.10.2; ipykernel 6.31.0.
Fresh installations should use Python 3.10 or newer and `requirements.txt`.
For matching scientific versions use `requirements-reproduced.txt`.

## What these checks do not demonstrate

No classifier has been trained this week. No disease accuracy, three-week forecast,
chemical deficiency, field deployment performance or real farm location is proven.
The synthetic 224-band cube and demonstration polygon are independent exercises.
