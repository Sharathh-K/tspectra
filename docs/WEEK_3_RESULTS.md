# Week 3 measured results

Compact CNN + vision transformer, trained from scratch on the existing Health/Other/Rust patches.

- Parameters: 24,407
- Training / validation: 480 / 120
- Accuracy: 0.7083; macro F1: 0.7066
- Week 2 accuracy: 0.6583; macro F1: 0.6346
- Logistic baseline accuracy: 0.6417; macro F1: 0.6446
- CPU run: 19.1 seconds; peak process memory: 351.9 MiB.
- Saved epoch: 11 of 16; selection by validation loss.
- Seed 42; batch 16; maximum 20 epochs; patience 5; Adam at 0.001.

## Artifacts

`hybrid_vit.pt` contains weights and architecture metadata. `preprocessing.npz` contains numeric scaling and PCA parameters. Reports retain checkpoint/manifest/preprocessing SHA-256 hashes, confusion matrix, class metrics, history and predictions for 120 validation and 300 unlabelled patches. Load via `terraspectra.model.load_model`; use `terraspectra.predict --model-dir models/week3` for real TIFF patches.

## Limits

One small development experiment; validation also selects the checkpoint. Source-related patch leakage is possible. No multi-seed significance claim, attention-only causal claim, independent-test result, calibrated probability, chemical diagnosis, pixel segmentation, farm geolocation or early forecasting claim. Spatial attention exchanges CNN features built from PCA components, not explicit original-wavelength tokens. The map and acreage analytics are synthetic and do not consume these predictions. Historical runtime comparisons are not controlled benchmarks.

## Delivery status

The 20-cell teaching notebook executed successfully, including a real local TIFF prediction and three chart images. The shared training command saved and reloaded the best transformer checkpoint before reporting metrics. TypeScript checking and the production frontend build passed; Vite retains its existing large-bundle warning. No separate test suite was added or run for this request. Live browser interactions and Mapbox rendering were not visually verified. The dashboard includes a no-token diagram fallback; actual farm registration remains unsupported.
