# Week 3 research and design decisions

## Primary sources

- [Vision Transformer paper, Dosovitskiy et al.](https://arxiv.org/abs/2010.11929): treating image patches as tokens motivates the token sequence, positional information and encoder. The paper's large-scale pretrained results do not transfer automatically to our 600 labelled agricultural patches. We implement a small CNN-token hybrid from scratch, not the paper's model or reported performance.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762): self-attention motivates comparison of tokens through multiple heads. Our heads compare image-region features, not directly named chemicals or physical wavelengths.
- [PyTorch 2.8 TransformerEncoderLayer](https://docs.pytorch.org/docs/2.8/generated/torch.nn.TransformerEncoderLayer.html): the installed version supports a compact encoder with `batch_first=True`, four heads and 32-dimensional tokens. The feature dimension must divide evenly by head count. One layer avoids unnecessary depth and compute for a small dataset.
- [HybridSN](https://arxiv.org/abs/1902.06701): combined 3D and 2D processing motivates retaining the existing compact spectral/spatial CNN before token projection. Our architecture and dataset differ; no published accuracy is claimed.
- [Scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): learned preprocessing must fit training data only. Week 3 reuses the same Week 1 preparation and manifest instead of fitting PCA on validation data.

## Why this design fits the available resources

The user's priority is understandable code and modest laptop cost. Sixteen tokens keep attention's pairwise interactions small (16 × 16 per head), and the 32-feature embedding keeps the model compact. All training runs use the existing PCA/pooled representation, two CPU threads and early stopping. This sacrifices some original spatial and spectral detail; it does not meet the project aspiration of processing full-resolution, 200+ band satellite scenes.

Spatial tokens contain mixed spectral features. Therefore the implementation meets a practical CNN + vision-attention milestone, while explicit original-band correlation analysis remains unsupported. An original-band transformer would require a different representation and its own controlled experiment.

The analytics calculations are independent of model predictions because the dataset lacks reliable links between patch files and the demonstration farm. Synthetic threshold acreage is a UI demonstration. Specific chemical anomalies cannot be obtained from the available class labels.

## Evaluation interpretation

Compare Week 2 CNN, Week 3 hybrid and logistic regression on the same fixed development split. Retain the earlier reports. Save checkpoint hashes, preprocessing hashes, hyperparameters and predictions. A positive change is not an attention-only causal effect, independent-test performance, or evidence of early warning. No hyperparameter sweep or selection among many seeds was performed for this delivery.
