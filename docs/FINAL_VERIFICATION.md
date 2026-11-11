# Final verification record

## Recomputed during the final review

- All 900 TIFF members were reread from the supplied ZIP and matched against extracted files and the manifest using SHA-256.
- All 900 prepared arrays had the expected finite float32 64×64×16 representation.
- Both saved model checkpoints, both numeric preprocessing artifacts, and the inventory matched their recorded fingerprints.
- Both models reproduced their saved confusion matrices on all 120 development-validation patches.
- All 80 synthetic grid cells passed the numerical boundary/corner/center checks.
- The 18-cell final notebook executed successfully and includes the model comparison chart.

See `reports/final_review/evidence.json` for the dated record. These are reproducibility checks on existing development evidence, not a new independent evaluation. No retraining or additional test set was introduced.

## Browser inspection during this review

The in-app browser displayed the separate Overview, Map & analytics, Inference, Model performance and Data quality views. Navigation changed the displayed content and page title; the selected heading received focus. Browser Back returned from Data quality to Inference. A narrow overview screenshot was inspected and saved as `reports/final_review/dashboard-overview.png`.

On the no-token map diagram, changing the simulated timeline from stage 3 to stage 1 changed the displayed score distribution. Moving the minimum-score control to 1.00 produced zero displayed cells and 0.0 selected acres. This confirms the observed diagram/analytics interaction, not every control or responsive breakpoint.

The Inference page showed the file control, mode selector and disabled submit button before file selection. No new browser upload was performed during this final UI pass. The earlier successful local patch and tiled API examples remain available in `reports/week4/api_demo.json` and are explicitly historical.

## Remaining verification limits

- No Mapbox token was configured; live satellite rendering, pan/tilt alignment and real-farm registration remain unverified.
- No new load, failure-case, GPU, giant-raster or multi-browser campaign was performed.
- The model evaluation remains a single-seed development split with possible source-related patch correlation.
- Historical reports may contain older UI labels and inspection limits; this document describes the final pass.

## Build

TypeScript checking and the Vite production build completed successfully. Vite reports the existing large JavaScript bundle warning. The warning does not prevent the build; download-size optimization remains future work.
