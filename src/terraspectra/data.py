"""Read the Week 1 manifest and make small, consistent model inputs."""
import csv
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

ROOT = Path(__file__).resolve().parents[2]
CLASS_NAMES = ["Health", "Other", "Rust"]


def read_inventory(root=ROOT):
    path = Path(root) / "reports/inventory.csv"
    if not path.exists():
        raise FileNotFoundError("Run the Week 1 preparation command first.")
    with path.open() as handle:
        return list(csv.DictReader(handle))


def make_input(cube):
    """Average each 4×4 square: (64,64,16) → (1,16,16,16). No learning here."""
    if cube.shape != (64, 64, 16) or not np.isfinite(cube).all():
        raise ValueError("Expected a finite (64, 64, 16) Week 1 PCA array.")
    small = cube.reshape(16, 4, 16, 4, 16).mean(axis=(1, 3))
    return torch.from_numpy(np.ascontiguousarray(small.transpose(2, 0, 1))).float().unsqueeze(0)


class PatchDataset(Dataset):
    """Cache only the small inputs: about 9.4 MiB for all 600 labelled patches."""

    def __init__(self, split, root=ROOT):
        self.rows = [row for row in read_inventory(root) if row["split"] == split]
        if not self.rows:
            raise ValueError(f"No images in split: {split}")
        inputs = []
        for row in self.rows:
            cube = np.load(Path(root) / "data/processed" / row["processed_path"], allow_pickle=False)
            inputs.append(make_input(cube))
        self.inputs = torch.stack(inputs)
        self.labels = torch.tensor([int(row["class_id"]) for row in self.rows], dtype=torch.long)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.inputs[index], self.labels[index]
