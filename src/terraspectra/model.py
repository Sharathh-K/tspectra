"""A small, HybridSN-inspired 3D–2D CNN. No transformer until Week 3."""
import torch
from torch import nn


class HybridCNN(nn.Module):
    """One (1, 16, 16, 16) PCA patch enters; three class scores leave."""

    def __init__(self):
        super().__init__()
        # Dimensions here mean (batch, channels, PCA depth, height, width).
        self.spectral_spatial = nn.Sequential(
            nn.Conv3d(1, 8, kernel_size=3, padding=1),
            nn.BatchNorm3d(8),
            nn.ReLU(),
            nn.Conv3d(8, 12, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm3d(12),
            nn.ReLU(),
        )
        # Fold 12 features × 8 depth positions into 96 channels for a 2D layer.
        self.spatial = nn.Sequential(
            nn.Conv2d(12 * 8, 24, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(24, 3),
        )

    def forward(self, x):
        if x.ndim != 5 or tuple(x.shape[1:]) != (1, 16, 16, 16):
            raise ValueError("Expected (batch, 1, 16, 16, 16). See data.py.")
        x = self.spectral_spatial(x)  # (batch, 12, 8, 8, 8)
        x = x.flatten(1, 2)          # (batch, 96, 8, 8)
        return self.spatial(x)       # logits: (batch, 3); loss applies softmax internally


def load_model(path):
    """Load only tensor weights and simple metadata, then switch to inference mode."""
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    model = HybridCNN()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, checkpoint
