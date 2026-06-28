"""Generate a SYNTHETIC Porto-Seguro-shaped dataset (placeholder).

The real Kaggle dataset is not downloaded yet. This produces a CSV with the real
Porto schema (id, target, ps_ind_*/ps_reg_*/ps_car_*/ps_calc_*) and a weak-signal,
imbalanced binary target, so the binary pipeline runs end-to-end. Reproducible
(fixed seed). Replace data/raw/porto_seguro_sample.csv with the real Kaggle
train.csv when available -- no config/code changes needed.

Usage:
    python scripts/make_porto_sample.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "porto_seguro_sample.csv"
N = 8000
rng = np.random.default_rng(42)


def cat(levels: list[int], missing_rate: float = 0.0) -> np.ndarray:
    vals = rng.choice(levels, size=N).astype(int)
    if missing_rate > 0:
        vals[rng.random(N) < missing_rate] = -1  # Porto encodes missing as -1
    return vals


df = pd.DataFrame({"id": np.arange(1, N + 1)})

# ind block
df["ps_ind_01"] = rng.integers(0, 8, N)
df["ps_ind_03"] = rng.integers(0, 12, N)
df["ps_ind_15"] = rng.integers(0, 14, N)
df["ps_ind_02_cat"] = cat([1, 2, 3, 4], missing_rate=0.02)
df["ps_ind_04_cat"] = cat([0, 1], missing_rate=0.01)
df["ps_ind_05_cat"] = cat([0, 1, 2, 3, 4, 5, 6], missing_rate=0.03)
df["ps_ind_06_bin"] = rng.integers(0, 2, N)
df["ps_ind_07_bin"] = rng.integers(0, 2, N)
df["ps_ind_08_bin"] = rng.integers(0, 2, N)  # extra column -> ignored by the config
df["ps_ind_16_bin"] = rng.integers(0, 2, N)
df["ps_ind_17_bin"] = rng.integers(0, 2, N)

# reg block
df["ps_reg_01"] = np.round(rng.uniform(0, 0.9, N), 1)
df["ps_reg_02"] = np.round(rng.uniform(0, 1.8, N), 1)
df["ps_reg_03"] = np.round(rng.uniform(0, 4, N), 3)

# car block
df["ps_car_01_cat"] = cat(list(range(12)), missing_rate=0.02)
df["ps_car_04_cat"] = cat(list(range(10)))
df["ps_car_07_cat"] = cat([0, 1], missing_rate=0.05)
df["ps_car_12"] = np.round(rng.uniform(0.2, 1.3, N), 4)
df["ps_car_13"] = np.round(rng.uniform(0.5, 3.5, N), 4)
df["ps_car_15"] = np.round(np.sqrt(rng.integers(0, 14, N)), 4)

# calc block
df["ps_calc_01"] = np.round(rng.uniform(0, 0.9, N), 1)
df["ps_calc_02"] = np.round(rng.uniform(0, 0.9, N), 1)
df["ps_calc_03"] = np.round(rng.uniform(0, 0.9, N), 1)  # extra column -> ignored
df["ps_calc_15_bin"] = rng.integers(0, 2, N)
df["ps_calc_16_bin"] = rng.integers(0, 2, N)

# Weak-signal, imbalanced binary target (a few features carry real signal).
logit = (
    -3.3
    + 0.45 * (df["ps_ind_05_cat"].clip(lower=0) > 0).astype(float)
    + 0.40 * (df["ps_car_07_cat"] == 0).astype(float)
    + 0.30 * df["ps_reg_02"]
    + 0.35 * df["ps_ind_17_bin"]
    + 0.25 * df["ps_ind_07_bin"]
    + rng.normal(0, 0.5, N)
)
prob = 1.0 / (1.0 + np.exp(-logit))
df["target"] = (rng.random(N) < prob).astype(int)

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"wrote {OUT}  shape={df.shape}  positive_rate={df['target'].mean():.3f}")
