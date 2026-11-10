# Week 2: teach a small model and colour a practice map

## The idea, like a stack of storybooks

Last week we made a big stack of 125 light-measurement pages into 16 summary pages
using PCA. This week a model learns to recognize patterns in those summary pages.
It chooses one answer for a whole image patch: **Health, Other or Rust**.

Separately, we build a map exercise. Imagine a farm drawn on squared paper. Each
square gets an invented number between zero and one. We colour low numbers green,
middle numbers amber and high numbers red. This teaches the dashboard how to display
a future response. These practice colours do not describe an actual farm's health.

Read `WEEK_2_RESEARCH.md` for sources and the reasons behind the choices. Open
`notebooks/02_week_two_model_and_heatmap.ipynb` for the same story with runnable cells.

## Part A — model architecture

### 1. Use the answers we actually have

The folders give us Health, Other and Rust labels. Health=0, Other=1, Rust=2. A label
describes the whole patch. We cannot claim to know the class of every tiny pixel,
and there are no chemical-deficiency labels. We use 480 training patches and keep
120 labelled patches for development validation. The other 300 have no answers.

### 2. Shrink the pictures without cutting away their edges

The input starts as 64×64×16. Average each little 4×4 square into one square.
The whole picture becomes 16×16×16. This is like replacing sixteen tiny tiles by one
tile with their average colour. It saves work but may hide small details.

Next arrange the stack for PyTorch: **batch, one channel, 16 pages, height, width**.
“Batch” means a small group of 16 pictures processed together. Our code checks shapes
so it cannot quietly confuse image width with spectral depth.

### 3. Let small filters explore the stack

A 3D convolution is a tiny moving window that looks across pages and across nearby
squares. Its filters learn useful patterns from practice examples. Two 3D layers
produce several pattern maps. Then we fold their page dimension into channels and
use a 2D convolution to study patterns across the image.

This is the hybrid: **3D first, 2D next**. It is a small design inspired by HybridSN,
not an exact copy of that research model. The transformer is a Week 3 experiment.

| Step | Shape, excluding batch | Meaning |
| --- | --- | --- |
| Week 1 PCA array | 64 × 64 × 16 | Image with 16 summary values per pixel |
| Average and reorder | 1 × 16 × 16 × 16 | One stack ready for a 3D layer |
| First 3D layer | 8 × 16 × 16 × 16 | Eight learned pattern stacks |
| Second 3D layer | 12 × 8 × 8 × 8 | Twelve smaller stacks |
| Fold features and depth | 96 × 8 × 8 | 96 pattern pages |
| 2D layer | 24 × 8 × 8 | Twenty-four spatial pattern maps |
| Average each pattern map | 24 | Twenty-four summary numbers |
| Classification head | 3 | Scores for Health, Other and Rust |

PCA pages are mixtures of wavelengths. Their neighbours are not necessarily
neighbouring wavelengths; keep that distinction when explaining the model.

### 4. Learn from mistakes

The model gives three scores. Cross-entropy measures how wrong it is about the known
answer. Backpropagation works out how to change its weights; Adam makes a small
update. One epoch means one pass through the 480 practice pictures.

Training is limited to 20 epochs. After each epoch we check the development set and
save the weights with the lowest validation loss. If the loss does not improve for
five checks, we stop early. We do not teach the model using validation gradients.
However, using validation to choose a checkpoint means it is not a final test.

Dropout randomly hides some features during training to discourage reliance on one
feature. Batch normalization stabilizes internal activations. During prediction,
`model.eval()` fixes normalization behaviour and disables dropout, while
`torch.inference_mode()` avoids storing training gradients.

### 5. Compare with a simple model

For the baseline, we describe each page with its average and its spread. That gives
32 numbers. Logistic regression learns a small classifier from them. Its scaler
learns from the training set only, just like Week 1 PCA.

Accuracy is the fraction of correct answers. Macro F1 averages a precision/recall
score equally across classes. The confusion matrix shows which answers got mixed up.
Our CNN slightly improves accuracy but has lower macro F1. It struggles with Health:
only 12 of 40 Health validation images are correctly recognized. We explain this
weakness rather than hide it behind one overall percentage.

## Part B — heatmap rendering

### 1. Make an honest practice response

`make_mock_heatmap.py` generates `frontend/public/mock-heatmap.json`. It contains
10 columns × 8 rows = 80 squares. Each square has an ID, row, column, four geographic
bounds and a simulated score. The response explicitly says it is mock data.

The squares sit inside the invented Week 1 farm boundary. GeoJSON uses longitude
first, latitude second. The first corner is repeated at the end to close each shape.
Rows start at the south and increase northward. The SVG diagram reverses the screen
row, because a screen's y coordinate increases downwards. Both views therefore put
the same northern cells at the top.

### 2. Turn the JSON into shapes

`heatmap.ts` checks the response: correct dimensions, scores within 0–1, unique IDs,
correct cell positions and aligned bounds. It makes a GeoJSON feature per cell.
Deck.gl's `GeoJsonLayer` draws each feature in the colour supplied by `scoreColor`.

We use cell polygons because the requirement is a coloured grid. Deck.gl's separately
named `HeatmapLayer` produces smoothed point-density blobs, which is a different
visual representation. The grid keeps each square's number easy to inspect.

### 3. Add controls

- **Show heatmap:** show or hide the coloured cells.
- **Farm boundary:** show or hide the outline.
- **Opacity:** make the colours more or less transparent.
- **Minimum score:** hide cells below that number; it does not change the scores.
- **Select a cell:** display its ID and invented value. The diagram also supports
  Tab followed by Enter or Space for keyboard selection.
- **Reset view:** return the Mapbox camera to its starting position.

The legend uses fixed ranges, so moving or zooming the map never changes what red
means. With no Mapbox token, an interactive diagram still works. With a token and
working WebGL, the same grid overlays the satellite map. MapboxOverlay synchronizes
the overlay when the camera moves. If loading or validation fails, the UI shows an
error rather than presenting invented success.

## Run it in VS Code

From the repository root, activate the Week 1 environment and install the update:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The completed training report and small model are included. You can open the notebook
and inspect them without training again. For a repeatable CPU training run:

```bash
PYTHONPATH=src python -m terraspectra.train --epochs 20 --batch-size 16 --patience 5 --device cpu
```

You need the Week 1 prepared arrays to retrain. The training command reuses the
480/120 split and overwrites the previous Week 2 artifacts. Save a copy first if you
want to compare separate experiments. CUDA can be requested explicitly on a machine
with a compatible installation. CPU is the tested Mac default.

Predict one raw TIFF using the supplied model and numeric preprocessing recipe:

```bash
PYTHONPATH=src python -m terraspectra.predict "data/raw/train/Health/hyper (1).tif"
```

The output is three uncalibrated class scores for a patch, not a pixel mask. This
command only handles the dataset's 64×64 patches; full-image tiling is Week 4.

Regenerate the mock response if needed:

```bash
PYTHONPATH=src python -m terraspectra.make_mock_heatmap
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Use the printed local URL. The diagram works immediately. Add your public Mapbox
token in `.env.local` as described in the README to use satellite tiles. The token
is not required to see the heatmap controls or measured model results.

## What to say in your internship review

“I built a small hybrid 3D–2D CNN and trained it using the Week 1 PCA arrays. I kept
the labelled validation split separate and compared against logistic regression.
The results are modest and show that Health and Rust need better discrimination.
I saved the model, preprocessing recipe, predictions and training metrics. I also
implemented a clickable, filterable heatmap from mock JSON, with matching diagram
and geographic renderers. The map cells are explicitly simulated and are independent
of the image predictions. Week 3 will investigate whether attention helps.”

See `WEEK_2_VALIDATION.md` for measured runtime, memory, checks and remaining limits.
