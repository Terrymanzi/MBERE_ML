"""SHAP analysis for the tree models (Random Forest, XGBoost).

Outputs, under <artifacts_dir>/reports/<model>/:
  * summary_plot.png    global feature impact (one-vs-rest, per class)
  * waterfall_plot.png  local explanation for a sample high-risk (Fatal) case
  * importance.csv      mean |SHAP| per encoded feature (descending)

The saved artifact is an imblearn Pipeline (encoder -> SMOTE -> classifier);
SHAP is computed on the classifier using the encoded test features.

Usage:
    python -m ml.explainability.shap_analysis --config ml/configs/addis.yaml --model xgboost
"""
from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shap  # noqa: E402

from ..training.common import load_processed  # noqa: E402
from ..utils.artifacts import load_model, report_dir, write_json  # noqa: E402
from ..utils.config import load_config  # noqa: E402
from ..utils.logging import get_logger  # noqa: E402
from ..utils.paths import PROJECT_ROOT  # noqa: E402

TREE_CLASSIFIERS = ("RandomForestClassifier", "XGBClassifier", "ExtraTreesClassifier",
                    "GradientBoostingClassifier", "LGBMClassifier")


def _unwrap(model):
    """Return (encoder, classifier) from an imblearn Pipeline artifact."""
    if not hasattr(model, "named_steps"):
        raise TypeError("SHAP analysis expects a Pipeline artifact (encoder -> ... -> classifier).")
    classifier = model.named_steps["classifier"]
    if type(classifier).__name__ not in TREE_CLASSIFIERS:
        raise TypeError(f"SHAP tree analysis supports tree models only, got {type(classifier).__name__}.")
    return model.named_steps["encoder"], classifier


def analyze(config, model_name: str, sample_size: int = 500, seed: int = 42) -> dict:
    logger = get_logger()
    encoder, classifier = _unwrap(load_model(config.paths.artifacts_dir / f"{model_name}.pkl"))

    X_df, y, class_names = load_processed(config, "test")
    X_enc = np.asarray(encoder.transform(X_df))
    feature_names = list(encoder.get_feature_names_out())

    # Subsample for tractable, readable plots.
    rng = np.random.default_rng(seed)
    if len(X_enc) > sample_size:
        idx = rng.choice(len(X_enc), size=sample_size, replace=False)
        X_enc, y = X_enc[idx], y[idx]
    X_sample = pd.DataFrame(X_enc, columns=feature_names)

    explainer = shap.TreeExplainer(classifier)
    explanation = explainer(X_sample, check_additivity=False)
    values = np.asarray(explanation.values)  # (n, f) [single-output] or (n, f, c)
    out = report_dir(config, model_name)

    # --- global summary + importance (robust to binary 2D / multiclass 3D) ---
    if values.ndim == 3:
        n_outputs = values.shape[2]
        per_output = [values[:, :, k] for k in range(n_outputs)]
        shap.summary_plot(
            per_output, X_sample, feature_names=feature_names,
            class_names=class_names[:n_outputs], show=False, max_display=20,
        )
        mean_abs = np.abs(values).mean(axis=(0, 2))
    else:  # binary single-output (SHAP for the positive class)
        shap.summary_plot(values, X_sample, feature_names=feature_names, show=False, max_display=20)
        mean_abs = np.abs(values).mean(axis=0)
    plt.title(f"SHAP summary — {model_name}")
    plt.tight_layout()
    plt.savefig(out / "summary_plot.png", dpi=120, bbox_inches="tight")
    plt.close("all")

    importance = (
        pd.DataFrame({"feature": feature_names, "mean_abs_shap": mean_abs})
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )
    importance.to_csv(out / "importance.csv", index=False)

    # --- local waterfall for a high-risk case (highest predicted positive/most-severe class) ---
    proba = classifier.predict_proba(X_sample.to_numpy())  # numpy: classifier was fit without feature names
    pos_col = proba.shape[1] - 1  # classes ordered ascending -> positive/most-severe last
    high_risk = int(np.argmax(proba[:, pos_col]))
    expl_i = explanation[high_risk]
    if np.asarray(expl_i.values).ndim == 2:  # multiclass -> pick the most-severe class
        expl_i = expl_i[:, expl_i.shape[-1] - 1]
    shap.plots.waterfall(expl_i, show=False, max_display=14)
    plt.title(f"SHAP waterfall — {model_name} — '{class_names[pos_col]}' case #{high_risk}")
    plt.tight_layout()
    plt.savefig(out / "waterfall_plot.png", dpi=120, bbox_inches="tight")
    plt.close("all")

    summary = {
        "model": model_name,
        "n_samples_explained": int(len(X_sample)),
        "n_encoded_features": len(feature_names),
        "high_risk_case_index": high_risk,
        "high_risk_positive_proba": float(proba[high_risk, pos_col]),
        "top_features": importance.head(10).to_dict(orient="records"),
    }
    write_json(summary, out / "shap_summary.json")
    logger.info("shap[%s]: wrote summary_plot.png, waterfall_plot.png, importance.csv -> %s",
                model_name, out)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="SHAP analysis for a tree model.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    parser.add_argument("--model", required=True, help="Tree model name (random_forest | xgboost).")
    parser.add_argument("--sample-size", type=int, default=500)
    args = parser.parse_args()
    analyze(load_config(args.config), args.model, sample_size=args.sample_size)


if __name__ == "__main__":
    main()
