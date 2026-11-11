# Recorded mid-project review results

The machine-readable source is `reports/mid_review/audit.json`; the frontend receives an identical copy. These are measurements on this Mac, not performance promises for other devices.

## Extraction

- All 900 TIFFs matched their ZIP contents and manifest SHA-256 hashes.
- All 900 processed arrays were finite float32 with shape 64 × 64 × 16.
- 741 raw TIFFs have 125 bands; 159 have 126 bands.
- Training / validation / unlabelled counts: 480 / 120 / 300.
- No exact file hash overlaps across splits. Related-patch leakage remains possible.
- None of the 900 TIFF CRSs resolved to a recognized EPSG code in this audit. This does not prove they contain no metadata; it prevents a justified claim of known farm placement.

## CPU memory

Each trial completed three optimizer steps with finite losses and gradients.

| Batch | Input-only MiB | Peak process RSS MiB |
|---|---:|---:|
| 1 | 0.015625 | 161.2 |
| 8 | 0.125 | 225.4 |
| 16 | 0.25 | 299.9 |
| 32 | 0.5 | 307.0 |

These are the final recorded run's measurements. Separate runs can differ because process memory residency and library allocation vary. Keep the current batch size 16; this is not a maximum-capacity benchmark. No GPU was used.

## GIS

All 80 synthetic cells passed independent Rasterio corner and center round-trip checks. Maximum observed corner discrepancy was 0 degrees, within the 1e-9-degree tolerance. The shared farm boundary matches the grid extent. Real-farm registration and live Mapbox rendering remain unverified; neither is represented as passed.

## Delivery checks

- The 18-cell review notebook executed successfully and includes two charts.
- TypeScript checking and the production frontend build passed.
- Vite retains the existing large JavaScript bundle warning; it did not prevent the build.
- The saved Week 2 model was not changed.

## Review decision

Proceed with Week 3 experiments on the small patch pipeline. Do not present the synthetic heatmap as real disease locations, the CPU audit as giant-satellite-cube capacity, or the split as an independent source-scene test. Follow the manual browser and real-georeferencing requirements in the review guide before upgrading those claims.
