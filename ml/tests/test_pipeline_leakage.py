"""REQUIRED: the imblearn pipeline must NOT resample the validation fold.

SMOTE lives inside an imblearn Pipeline. Samplers run only during ``fit`` (on
the training fold) and are bypassed at ``predict``/``transform`` time, so the
validation/test data is never resampled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

# Module-level record so it survives sklearn clone() of the sampler.
RESAMPLE_CALLS: list[tuple[int, int]] = []


class SpySMOTE(SMOTE):
    """SMOTE that records (input_size, output_size) on each fit_resample call."""

    def fit_resample(self, X, y):
        X_res, y_res = super().fit_resample(X, y)
        RESAMPLE_CALLS.append((len(X), len(X_res)))
        return X_res, y_res


def _imbalanced_data():
    rng = np.random.default_rng(0)
    n0, n1 = 80, 20  # imbalanced 2-class for a clean SMOTE demonstration
    X = pd.DataFrame({
        "f1": np.concatenate([rng.normal(0, 1, n0), rng.normal(3, 1, n1)]),
        "f2": np.concatenate([rng.normal(0, 1, n0), rng.normal(-3, 1, n1)]),
    })
    y = np.array([0] * n0 + [1] * n1)
    return X, y


def test_smote_resamples_train_fold_only():
    RESAMPLE_CALLS.clear()
    X, y = _imbalanced_data()

    # explicit train/validation split
    rng = np.random.default_rng(1)
    perm = rng.permutation(len(y))
    train_idx, val_idx = perm[:70], perm[70:]

    pipe = Pipeline([
        ("smote", SpySMOTE(k_neighbors=3, random_state=0)),
        ("clf", LogisticRegression(max_iter=500)),
    ])
    pipe.fit(X.iloc[train_idx], y[train_idx])

    # SMOTE was called exactly once — during fit, on the training fold.
    assert len(RESAMPLE_CALLS) == 1
    in_size, out_size = RESAMPLE_CALLS[0]
    assert in_size == len(train_idx)     # it saw the train fold
    assert out_size > len(train_idx)     # ...and upsampled it

    # Predicting the validation fold must NOT trigger any resampling.
    preds = pipe.predict(X.iloc[val_idx])
    assert len(RESAMPLE_CALLS) == 1          # still one call — no resample on validation
    assert len(preds) == len(val_idx)        # validation fold size is unchanged


def test_pipeline_predict_proba_matches_validation_size():
    RESAMPLE_CALLS.clear()
    X, y = _imbalanced_data()
    pipe = Pipeline([
        ("smote", SpySMOTE(k_neighbors=3, random_state=0)),
        ("clf", LogisticRegression(max_iter=500)),
    ])
    pipe.fit(X, y)
    proba = pipe.predict_proba(X)
    # one fit-time resample; scoring never resamples
    assert len(RESAMPLE_CALLS) == 1
    assert proba.shape == (len(X), 2)
