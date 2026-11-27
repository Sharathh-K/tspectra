import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

DATA_FILE = "data/processed_train.npz"
MODEL_FILE = "model_3dcnn.pt"
EPOCHS = 20
BATCH = 16
LR = 1e-3
SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)

d = np.load(DATA_FILE)
X, y, classes = d["X"], d["y"], [str(c) for c in d["classes"]]
print("data:", X.shape, "classes:", classes)

# 80/20 split that keeps the same class balance in both parts
Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)

# normalise each PCA component using training data only
mean = Xtr.mean(axis=(0, 2, 3), keepdims=True)
std = Xtr.std(axis=(0, 2, 3), keepdims=True) + 1e-6
Xtr = (Xtr - mean) / std
Xva = (Xva - mean) / std

# 3D-CNN wants (batch, channel, depth, height, width): depth = the 10 PCA components
Xtr = torch.tensor(Xtr).unsqueeze(1)
Xva = torch.tensor(Xva).unsqueeze(1)
ytr = torch.tensor(ytr, dtype=torch.long)
yva = torch.tensor(yva, dtype=torch.long)
print("train:", tuple(Xtr.shape), "val:", tuple(Xva.shape))


def block(cin, cout, pool):
    return nn.Sequential(
        nn.Conv3d(cin, cout, kernel_size=3, padding=1),
        nn.BatchNorm3d(cout),
        nn.ReLU(),
        pool,
    )


class Spectral3DCNN(nn.Module):
    def __init__(self, n_classes=3):
        super().__init__()
        self.features = nn.Sequential(
            block(1, 8, nn.MaxPool3d((1, 2, 2))),
            block(8, 16, nn.MaxPool3d((2, 2, 2))),
            block(16, 32, nn.AdaptiveAvgPool3d(1)),
        )
        self.drop = nn.Dropout(0.3)
        self.fc = nn.Linear(32, n_classes)

    def forward(self, x):
        x = self.features(x).flatten(1)
        return self.fc(self.drop(x))


model = Spectral3DCNN(len(classes))
opt = torch.optim.Adam(model.parameters(), lr=LR)
loss_fn = nn.CrossEntropyLoss()


def predict(xs):
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(xs), 64):
            out.append(model(xs[i:i + 64]).argmax(1))
    return torch.cat(out)


best = 0.0
for ep in range(1, EPOCHS + 1):
    model.train()
    perm = torch.randperm(len(Xtr))
    total = 0.0
    for i in range(0, len(Xtr), BATCH):
        idx = perm[i:i + BATCH]
        xb, yb = Xtr[idx], ytr[idx]
        if torch.rand(1) < 0.5:
            xb = torch.flip(xb, dims=[3])  # random left-right flip
        if torch.rand(1) < 0.5:
            xb = torch.flip(xb, dims=[4])  # random up-down flip
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
        total += loss.item() * len(idx)
    acc = (predict(Xva) == yva).float().mean().item()
    print(f"epoch {ep:2d}/{EPOCHS}  train loss {total / len(Xtr):.4f}  val acc {acc:.3f}")
    if acc > best:
        best = acc
        torch.save({"state": model.state_dict(), "mean": mean, "std": std, "classes": classes}, MODEL_FILE)

print("best val acc:", round(best, 3), "| saved", MODEL_FILE)

ckpt = torch.load(MODEL_FILE, weights_only=False)
model.load_state_dict(ckpt["state"])
pred = predict(Xva).numpy()
print("classes:", classes)
print("confusion matrix (rows = true, cols = predicted):")
print(confusion_matrix(yva.numpy(), pred))
