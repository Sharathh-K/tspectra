# Week 1 — Data preparation and map foundation

## Objective

The first milestone was to understand the supplied hyperspectral dataset, prepare it for machine learning, and build the geographic dashboard foundation. This report describes completed work recorded in the repository; week numbers refer to project milestones rather than calendar dates.

## Work completed

I inspected the Beyond Visible Spectrum: AI for Agriculture ZIP before choosing the preprocessing steps. It contains 900 TIFF patches, each 64 × 64 pixels. There are 600 labelled images, divided equally into Health, Other and Rust, and 300 unlabelled images. I used Rasterio to read the files and recorded dimensions, labels, coordinate metadata and file fingerprints in an inventory.

The files did not all have identical band counts: 741 contained 125 bands and 159 contained 126. The extra plane in the latter files contained only binary values of 0 and/or 65,535. The preparation code checks that condition before removing it, leaving 125 usable bands. It does not assume that the extra plane is a disease mask.

I created a repeatable split of 480 training and 120 development-validation patches, with equal class representation. The 300 unlabelled patches were kept separate. StandardScaler and PCA were fitted using sampled pixels from the training partition only. The same saved transformation reduced every image to 16 PCA components, stored as float32 arrays of shape 64 × 64 × 16.

For the interface, I created a React dashboard with Mapbox GL JS and a synchronized Deck.gl farm-boundary overlay. The boundary is an invented rectangle near Bengaluru. A separate synthetic 224-band GeoTIFF demonstrates the larger-band processing requested in the brief without altering the real training data.

## Simple explanation

A hyperspectral image is like a book with 125 pages. Each page contains a different light measurement. PCA produces 16 summary pages so a small model can work with less data. The map is the noticeboard on which geographic layers can later be displayed.

## Results and learning

The main deliverables were a dataset inventory, repeatable split, reusable scaling/PCA recipe, compact arrays, an explanatory notebook and the map scaffold. Fitting preprocessing only on training examples avoids teaching it from the validation answers. PCA components are mixtures of bands, and retained variance is not classification accuracy.

## Limitations and next step

The real dataset has 125 usable bands, not 200+. Its coordinate metadata does not justify placing patches on the demonstration farm. Satellite tiles require a Mapbox token; live satellite alignment was not verified. The next milestone was to train a patch classifier and develop a mock heatmap.

## Supporting material

- [Preparation guide](../WEEK_1_GUIDE.md)
- [Preparation notebook](../../notebooks/01_week_one_data_preparation.ipynb)
- [Original verification record](../VALIDATION.md)
