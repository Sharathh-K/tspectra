# Week 1: understand the pictures, prepare the data, and draw a farm

## The idea, explained simply

Imagine a normal photograph as three transparent pages: red, green and blue.
Our hyperspectral picture is a stack of **125 pages**. Each page measures a different
part of light. A pixel is one tiny square with 125 numbers inside it.

We have two jobs this week:

1. Organize and simplify these stacks so next week's model can read them.
2. Build a map and draw a practice farm boundary on it.

The map is like an empty noticeboard. This week we hang the farm outline on it.
Later we can add model results when we have suitable data and trustworthy locations.

## What the supplied plan asks for

The first screenshot describes the long-term goal. The second splits that goal into
weeks. Week 1 is **Rasterio data loading, PCA, and a React / Mapbox / Deck.gl map**.
We implement those first. Model training begins in Week 2; API inference and disease
heatmaps belong to later weeks. There is no disease score or claimed forecast here.

The plan mentions mock cubes with over 200 bands. Your real Kaggle data has 125.
We preserve its real bands. `make_mock_cube.py` separately creates a clearly synthetic
224-band GeoTIFF to demonstrate reading a larger georeferenced cube. It is never
mixed into disease training. TIFF is a container, not a promise of usable geography.

## Step 1: unpack and count the real images

The preparation command extracts your ZIP into `data/raw/`. It does not modify the
downloaded ZIP. It reads the images one at a time instead of loading the whole dataset.

There are 600 labelled training images: 200 each in `Health`, `Other`, and `Rust`.
The other 300 files are in `val/val`. Their class names are **not supplied**.
The folder name `val` alone cannot give us the correct answers for evaluation.

`Other` is a competition category. It is not a diagnosed chemical deficiency.
The inventory records the original path, label, dimensions, data type, coordinate
metadata and a file fingerprint. This is our packing list: we can find every image
again and identify exact copies.

## Step 2: put the image axes in a familiar order

Rasterio reads `(bands, height, width)`. We rearrange it to
`(height, width, bands)`: a picture whose every square contains a list of measurements.
We retain the actual height and width of every file. Invalid or missing values cause
a clear error; we do not silently replace missing measurements with fake zeros.

Inspection revealed 741 TIFFs with 125 bands and 159 TIFFs with 126 bands. The extra
last band contains only 0 and/or 65,535: 154 are constant 65,535, three are constant
zero, and two contain both values. We verify this binary-value condition before
removing the plane; any unexpected content stops preparation. We preserve
the original band count and a removal flag in the inventory. We do not assume the
undocumented plane is a disease mask or a real wavelength.

Raw numbers are sensor values. We do not claim that dividing by 10,000 magically
converts this download to calibrated reflectance. No exact wavelength table is
provided in these files, so the notebook uses **band index** on its spectral axis.

## Step 3: keep some answers aside

We split the 600 labelled files into 480 training and 120 development-validation
images. Each class contributes 160 training and 40 validation files. Seed 42 makes
this repeatable. The 300 unlabelled files remain separate for later inference.

Think of training as practice questions and validation as questions saved for checking.
The checks must not teach the preparation step. Exact copies crossing partitions
cause an error. Neighbouring patches may still come from the same source scene:
without reliable scene/date IDs, this is only a **patch-level development split**.
It cannot establish performance on a new farm, season, or satellite.

## Step 4: scale the bands and teach PCA

Some pages have larger numbers than others. StandardScaler learns a mean and spread
for each band from a small sample of training pixels. It puts the bands on comparable
scales. We sample at most 64 pixels from each training image: normally 30,720 pixels.

PCA finds common patterns across these measurements and makes 16 new summary pages.
These are weighted mixtures of the original bands, not 16 selected wavelengths.
PCA does not know which pictures are healthy or rusty. It preserves variation, which
may include lighting and background. Retained variance is **not disease accuracy**.

Both scaler and PCA learn **only from the training sample**. We save them together
in `reports/preprocessing.joblib`. The identical fitted transformation is applied to
training, development-validation and unlabelled images. We never fit another PCA
for validation. This is what keeps the preparation fair and reproducible.

Each result is saved as a float32 NumPy file with `(height, width, 16)` dimensions.
The CSV tells next week's code where it belongs and which label it has. This lets us
start with a smaller model and avoid a large GPU requirement in Week 1.

## Step 5: make the map scaffold

React builds the dashboard shell. Mapbox GL JS loads the satellite basemap and handles
dragging, zooming, pitch and rotation. Deck.gl draws the farm polygon on an overlay.
`MapboxOverlay` automatically keeps its camera aligned with Mapbox's camera, so there
are not two independent camera states to keep in sync.

The practice boundary is an invented rectangle near Bengaluru, stored in `farm.ts`.
GeoJSON coordinate pairs are **[longitude, latitude]**. The first and last corner are
the same, which closes the outline. A checkbox toggles the boundary and Reset view
returns to its starting position. These are geographic UI demonstrations only.

The Kaggle TIFFs contain an unknown CRS and unusual units/transform. We preserve
that metadata in the inventory, but have no evidence that it places patches on a
real farm. We never attach the image patches to our invented boundary, calculate
real acres at risk, or invent a disease heatmap.

A public Mapbox access token is required for satellite tiles. Without one, the app
shows an explicit setup placeholder. This is not a substitute satellite map. The
dashboard's image counts and PCA variance come from the actual preparation report.

## How to explain this in your internship review

“I inspected the downloaded files before coding. The dataset has 125 spectral bands,
600 labelled patches and 300 unlabelled patches. I created a repeatable labelled
development split, fitted scaling and PCA on training pixels only, and saved reusable
transformations and compact arrays. I also built a React map scaffold with a Mapbox
basemap and a synchronized Deck.gl demonstration boundary. The map does not claim to
geolocate the competition patches. Disease training is the next step.”

## Week 1 completion checklist

- Open and run `notebooks/01_week_one_data_preparation.ipynb` using the project environment.
- Read `reports/dataset_summary.json` and inspect `reports/inventory.csv`.
- Inspect one original cube, its spectral curve, PCA preview and variance plot.
- Confirm raw and processed arrays retain the same spatial dimensions.
- Save the reusable scaler and PCA. Never upload raw data or fitted binary artifacts.
- Run the React app. With your own Mapbox token, check pan, zoom, rotation, boundary
  toggle and reset. A real map-token check needs your token and internet access.
- Read `docs/VALIDATION.md` for what was actually run in this delivery.

## Sources

- Project requirements: the two screenshots you supplied.
- Downloaded data: https://www.kaggle.com/competitions/beyond-visible-spectrum-ai-for-agriculture-P1/data
- Rasterio array reading: https://rasterio.readthedocs.io/en/stable/topics/reading.html
- PCA: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- Deck.gl map synchronization: https://deck.gl/docs/api-reference/mapbox/mapbox-overlay
- Mapbox setup: https://docs.mapbox.com/mapbox-gl-js/guides/get-started/
