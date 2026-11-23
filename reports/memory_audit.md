# TerraSpectra memory audit

**November 23 review · Mock field · CPU training**

The largest observed process working set was **434.9 MiB** during the first HybridSN training step. Creating the network and Adam optimizer produced the largest increase within a stage, **81.9 MiB**. Building the patch view added less than 0.1 MiB to the observed working set. On this mock scene, model setup and training mattered more to peak memory than storing the image.

## What was measured

[Notebook 07](../notebooks/07_memory_audit.ipynb) ran in a fresh Windows x64 Jupyter kernel with CPU PyTorch 2.15.0 and four PyTorch threads. It read the 67 × 67 × 200 float32 HDF5 cube, selected 166 wavelengths and fitted ten whitened PCA components on the 2,546 valid training pixels in rows 0–37. The loader assembled 64 patches of size 9 × 9 for a forward pass, backward pass and Adam update.

The sampler recorded resident set size at each stage boundary and approximately every 5 ms in between. Values include imported libraries, live arrays and allocator caches. Short-lived peaks can escape sampling. The initial 315.9 MiB includes the loaded notebook runtime. Increases depend on initialization and on what earlier stages retain.

| Stage | Entry (MiB) | Observed peak (MiB) | Increase above entry (MiB) |
|---|---:|---:|---:|
| Read cube and select bands | 315.9 | 328.9 | 13.0 |
| Fit PCA and transform training rows | 327.1 | 343.1 | 15.9 |
| Pad training region and form window view | 339.2 | 339.2 | 0.0 |
| Collate 64 patches | 339.2 | 341.1 | 1.9 |
| Create network and Adam | 341.1 | 423.0 | 81.9 |
| First forward, backward and update | 423.0 | 434.9 | 11.9 |

Values were rounded independently. The model setup measurement includes first-use library costs. This run covers one CPU training batch and excludes notebook 06’s teaching examples, validation passes and GPU memory.

## What grows with scene size

The mock reflectance cube held **3.425 MiB** of data. The training windows shared a **0.132 MiB** padded array. Copying those windows would have required **7.867 MiB**. One 64-patch input tensor held **0.198 MiB**, before labels, intermediate activations and gradients.

For a hypothetical 1,000 × 1,000 scene at the same band count, a float32 reflectance cube would occupy **762.939 MiB** and a ten-component score image **38.147 MiB**. Materializing all 9 × 9 × 10 patches would require **3,089.905 MiB** (3.02 GiB) for patch values alone. These are calculated array sizes. A full-scene peak also depends on simultaneous copies, preprocessing workspaces and the training runtime.

For a larger scene, read HDF5 spatial windows, apply the fitted scaler and PCA in blocks, and assemble patches on demand. Keep a four-pixel halo around each tile so interior edge centres can use their neighbours. Preserve the training/validation boundary when padding. With batch size fixed at 64, the input tensor stays at 0.198 MiB while scene dimensions grow. A representative tile run would establish the working-set budget for that scene.
