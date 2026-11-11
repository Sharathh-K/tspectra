# Final review research notes

The final pass focuses on defensible evaluation and maintainable delivery. Earlier domain and implementation references remain in the Week 2–4 research documents.

- [Scikit-learn: cross-validation and model selection](https://scikit-learn.org/stable/modules/cross_validation.html): validation used for model selection must be distinguished from an independent final test. Recomputing the same split confirms reproducibility, not generalization. Accordingly, the final report retains the term development validation.
- [React: conditional rendering](https://react.dev/learn/conditional-rendering): separate components can be shown for each selected view. We use five hash-addressed page views to keep the UI focused without introducing a routing dependency.
- [React: preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state): removing a component resets its local state. The guide explains that navigation resets map controls and the upload form rather than promising persistence.
- [Rasterio: windowed reading and writing](https://rasterio.readthedocs.io/en/latest/topics/windowed-rw.html): source block sizes affect actual reads, so a windowed algorithm does not by itself prove a fixed maximum memory footprint for every raster.
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/): the saved model is loaded once per service process, supporting the existing single-worker local design.

The project brief is an aspiration, not evidence that the supplied dataset has 200+ bands, chemical targets, chronological observations or surveyed farm coordinates. Final acceptance is therefore recorded per capability. Real dataset results, synthetic demonstrations and unverified aspirations are never combined into a single accuracy or completion claim.
