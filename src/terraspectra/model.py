"""Compact Week 2 CNN and Week 3 CNN–vision-transformer models."""
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
    model = HybridViT() if checkpoint.get("architecture") == "hybrid_vit" else HybridCNN()
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, checkpoint


class HybridViT(nn.Module):
    """CNN features become 16 image tokens; attention lets them share information."""

    def __init__(self):
        super().__init__()
        self.features = HybridCNN().spectral_spatial
        # Each token carries features from all eight reduced depth positions.
        self.tokens = nn.Conv2d(96, 32, kernel_size=2, stride=2)
        self.position = nn.Parameter(torch.zeros(1, 16, 32))
        nn.init.normal_(self.position, std=0.02)
        self.attention = nn.TransformerEncoderLayer(
            d_model=32, nhead=4, dim_feedforward=64, dropout=0.1,
            activation="gelu", batch_first=True)
        self.classifier = nn.Sequential(nn.LayerNorm(32), nn.Linear(32, 3))

    def forward(self, x):
        if x.ndim != 5 or tuple(x.shape[1:]) != (1, 16, 16, 16):
            raise ValueError("Expected (batch, 1, 16, 16, 16)")
        features = self.features(x).flatten(1, 2)  # (batch, 96, 8, 8)
        tokens = self.tokens(features).flatten(2).transpose(1, 2)  # (batch, 16, 32)
        tokens = self.attention(tokens + self.position)
        return self.classifier(tokens.mean(dim=1))
