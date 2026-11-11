# Week 4 research and engineering decisions

## Primary sources consulted

1. [FastAPI lifespan events](https://fastapi.tiangolo.com/advanced/events/): load shared model resources during application startup rather than loading a checkpoint on every request. This keeps the local service easy to understand.
2. [Starlette request streaming](https://www.starlette.dev/requests/): streaming exposes body chunks without requiring the entire body in memory. We write chunks to a temporary file with a byte limit. The API deliberately uses raw binary uploads rather than multipart forms; the frontend and curl example match that contract.
3. [FastAPI concurrency](https://fastapi.tiangolo.com/async/): CPU-bound work is different from waiting for I/O. We dispatch inference to a thread and bound simultaneous jobs. This does not make inference inherently faster or provide GPU acceleration.
4. [Rasterio windowed reading and writing](https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html): window offsets let us read and write parts of a raster. Source block layout can impose larger reads, so “one model tile at a time” must not be advertised as an absolute RAM bound.
5. [Rasterio georeferencing](https://rasterio.readthedocs.io/en/latest/topics/georeferencing.html): transforms and CRS describe raster placement. We preserve source metadata but do not turn nonstandard dataset coordinates into verified farm locations.

## Choices specific to this dataset

The saved classifier accepts 64×64×125 patches through the existing PCA/pooling pipeline. Nonoverlapping windows match that patch contract and simplify stitching. Partial windows repeat edge values and crop writes to source dimensions. No retraining is needed, but edge padding and new scene resolutions are not validated scientifically.

The model outputs one class score vector per patch. Writing the vector into every pixel is an explicit visualization convention, not pixel segmentation. Neither the TIFF output nor the API can supply chemical measurements, dates, or spatial ground truth missing from training data.

The repository already records the 900-file extraction audit. The Week 4 demonstration uses an artificial mosaic of those real patches to exercise window placement and partial edges, rather than claiming that it is a satellite acquisition. The four timeline stages are deterministic mock score multipliers with no calendar dates. Upload predictions are not inserted into that unrelated farm map.

## Scope and performance

CPU-only, one local Uvicorn worker, two PyTorch threads, 128 MiB upload cap and 256 API tiles. The CLI offers a separate adjustable tile limit. Temporary storage and outputs consume disk space; windowed access does not eliminate storage needs. No stress, concurrent-load or GPU-throughput benchmark is claimed. FastAPI 0.128.8 and Uvicorn 0.39.0 were installed in the project environment; exact versions are recorded for reproduction.
