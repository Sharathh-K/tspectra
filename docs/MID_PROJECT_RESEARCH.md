# Research behind the mid-project review

Research question: what evidence can we honestly provide for the screenshot's memory and GIS requirements, using this ZIP and existing implementation?

## Primary references and decisions

1. [PyTorch profiler documentation](https://docs.pytorch.org/docs/stable/profiler.html) and [profiler recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe): operator memory tracking can diagnose tensor allocations. Our review reports operating-system process peak RSS instead, because the user's laptop must accommodate the entire process. We do not label RSS as a PyTorch allocator peak or add operator allocation totals and call them peak memory.
2. [Python resource.getrusage](https://docs.python.org/3/library/resource.html): process resource usage provides a maximum RSS field. Units vary by platform; the code converts macOS bytes and Linux KiB explicitly. This script targets the user's macOS environment and Linux, not native Windows. A fresh process per batch avoids carrying a larger previous trial's lifetime high-water mark into a later trial.
3. [Rasterio georeferencing](https://rasterio.readthedocs.io/en/latest/topics/georeferencing.html): a CRS and a transform together describe geographic placement. A TIFF extension or a nonempty CRS string alone does not establish trustworthy farm coordinates.
4. [Rasterio transform API](https://rasterio.readthedocs.io/en/stable/api/rasterio.transform.html): `from_bounds`, `xy`, and `rowcol` provide independently calculated cell corners and center round-trips. North-origin raster rows must be reconciled with our south-origin mock JSON rows.
5. [RFC 7946, GeoJSON](https://www.rfc-editor.org/rfc/rfc7946): geographic positions use longitude then latitude. We preserve that order and closed polygon rings for the demonstration farm.
6. [Deck.gl MapboxOverlay](https://deck.gl/docs/api-reference/mapbox/mapbox-overlay): the overlay synchronizes with the base map's camera. The existing integration is appropriate; live visual alignment remains a distinct check requiring an actual browser, token and map rendering.

## Evidence boundaries

The 900-file integrity scan and CPU trials use the supplied data. GIS calculations use the explicitly synthetic grid and boundary. We do not infer a relationship between those two coordinate spaces. Zero duplicate SHA-256 hashes cannot rule out related neighbouring patches. Three training steps per batch are a bounded feasibility demonstration, not a stress test of arbitrarily large imagery. No accuracy improvement or new forecasting capability is claimed during this review.

The actual report records the installed PyTorch version. Web documentation may describe newer releases; the audit uses basic operations already present in the installed environment and records the results from that environment.
