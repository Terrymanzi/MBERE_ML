"""Evaluate any saved model on the held-out test set.

Produces, under <artifacts_dir>/reports/<model>/:
  * confusion_matrix.png
  * roc_curves.png   (one-vs-rest per class)
  * metrics.json     (directly comparable across models)

Usage:
    python -m ml.evaluation.evaluate --config ml/configs/addis.yaml --model xgboost
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")  # headless: write PNGs without a display
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import ConfusionMatrixDisplay, roc_auc_score, roc_curve  # noqa: E402

from ..training.common import load_processed  # noqa: E402
from ..utils.artifacts import load_model, report_dir, write_json  # noqa: E402
from ..utils.config import load_config  # noqa: E402
from ..utils.logging import get_logger  # noqa: E402
from ..utils.paths import PROJECT_ROOT  # noqa: E402
from .metrics import align_proba, compute_metrics  # noqa: E402


def plot_confusion_matrix(y_true, y_pred, class_names, path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true, y_pred, labels=list(range(len(class_names))),
        display_labels=class_names, cmap="Blues", ax=ax, colorbar=False,
    )
    ax.set_title("Confusion matrix")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_roc_curves(y_true, y_proba, class_names, path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    for i, name in enumerate(class_names):
        y_bin = (np.asarray(y_true) == i).astype(int)
        if y_bin.sum() == 0 or y_bin.sum() == len(y_bin):
            continue
        fpr, tpr, _ = roc_curve(y_bin, y_proba[:, i])
        auc = roc_auc_score(y_bin, y_proba[:, i])
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", linewidth=1)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("ROC curves (one-vs-rest)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def evaluate_model(config, model_name: str) -> dict:
    logger = get_logger()
    model = load_model(config.paths.artifacts_dir / f"{model_name}.pkl")
    X, y, classes = load_processed(config, "test")

    y_pred = np.asarray(model.predict(X))
    y_proba = align_proba(model.predict_proba(X), model.classes_, config.n_classes)

    metrics = compute_metrics(y, y_pred, y_proba, classes)
    metrics["model"] = model_name

    out = report_dir(config, model_name)
    plot_confusion_matrix(y, y_pred, classes, out / "confusion_matrix.png")
    plot_roc_curves(y, y_proba, classes, out / "roc_curves.png")
    write_json(metrics, out / "metrics.json")

    logger.info("evaluate[%s]: f1_macro=%.4f recall_macro=%.4f roc_auc_ovr=%.4f -> %s",
                model_name, metrics["f1_macro"], metrics["recall_macro"],
                metrics["roc_auc_ovr_macro"] or float("nan"), out)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved model on the test set.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    parser.add_argument("--model", required=True, help="Model name (e.g. baseline, random_forest, xgboost).")
    args = parser.parse_args()
    evaluate_model(load_config(args.config), args.model)


if __name__ == "__main__":
    main()
