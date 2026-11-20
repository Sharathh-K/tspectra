import glob
import os
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score

DATA_DIR = "data/train"
CLASSES = ["Health", "Other", "Rust"]
N_BANDS = 125
SEED = 42

feats, labels = [], []
for idx, cls in enumerate(CLASSES):
    for f in sorted(glob.glob(os.path.join(DATA_DIR, cls, "*.tif"))):
        with rasterio.open(f) as src:
            a = src.read().astype("float32")[:N_BANDS]  # drop the extra 126th band
        feats.append(np.concatenate([a.mean(axis=(1, 2)), a.std(axis=(1, 2))]))
        labels.append(idx)
X, y = np.array(feats), np.array(labels)
print("features:", X.shape)

# same split as train_model.py, so the 120 test patches are identical
Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
rf = RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=-1).fit(Xtr, ytr)
pred = rf.predict(Xva)
print("random forest val acc:", round(float((pred == yva).mean()), 3))
print("confusion matrix (rows = true, cols = predicted):")
print(confusion_matrix(yva, pred))

cv = cross_val_score(RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=-1), X, y, cv=5)
print("5-fold accuracy on all 600:", round(float(cv.mean()), 3), "+/-", round(float(cv.std()), 3))
