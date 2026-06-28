"""Multiclass-aware metrics (no plotting deps, so training can import it).

Headline metrics for this imbalanced problem are F1 (macro), recall, and
ROC-AUC (one-vs-rest); accuracy is reported but NOT treated as headline.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
    roc_auc_score,
)


def align_proba(proba: np.ndarray, model_classes, n_classes: int) -> np.ndarray:
    """Reorder predict_proba columns to canonical 0..n_classes-1 order."""
    proba = np.asarray(proba)
    aligned = np.zeros((proba.shape[0], n_classes), dtype=float)
    for col, cls in enumerate(model_classes):
        aligned[:, int(cls)] = proba[:, col]
    return aligned


def _roc_auc_ovr(y_true: np.ndarray, y_proba: np.ndarray, labels: list[int], names: list[str]) -> dict:
    macro = None
    try:
        if len(labels) == 2:  # binary: score the positive class
            macro = float(roc_auc_score(y_true, y_proba[:, 1]))
        else:
            macro = float(roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro", labels=labels))
    except ValueError:
        macro = None

    per_class = {}
    for i in labels:
        y_bin = (y_true == i).astype(int)
        if y_bin.sum() == 0 or y_bin.sum() == len(y_bin):
            per_class[names[i]] = None
            continue
        try:
            per_class[names[i]] = float(roc_auc_score(y_bin, y_proba[:, i]))
        except ValueError:
            per_class[names[i]] = None
    return {"macro": macro, "per_class": per_class}


def compute_metrics(y_true, y_pred, y_proba, class_names: list[str]) -> dict:
    """Confusion matrix, per-class & macro precision/recall/F1, ROC-AUC (OVR)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    y_proba = np.asarray(y_proba)
    labels = list(range(len(class_names)))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    roc = _roc_auc_ovr(y_true, y_proba, labels, class_names)

    per_class = {}
    for i in labels:
        per_class[class_names[i]] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
            "roc_auc_ovr": roc["per_class"].get(class_names[i]),
        }

    return {
        "n_samples": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),  # reported, NOT headline
        "f1_macro": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "precision_macro": float(precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "roc_auc_ovr_macro": roc["macro"],
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "labels": list(class_names),
    }
