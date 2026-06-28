#!/usr/bin/env python
"""Single reproducible entry point for the mbere-ml pipeline.

    python train.py --config ml/configs/addis.yaml [--model rf|xgb|baseline|all]

Runs: load -> clean -> engineer features -> split -> train (SMOTE inside CV, on
the train fold only) -> evaluate -> SHAP -> save versioned artifact + report.

Everything for a run is written under:
    ml/artifacts/runs/{timestamp}_{git-short-sha}/

This is a THIN wrapper: all logic lives in the ml/ package. Re-running with the
same config + seed reproduces identical metrics (only the run directory name,
which carries a timestamp, differs).
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.evaluation.evaluate import evaluate_model  # noqa: E402
from ml.models import make_baseline  # noqa: E402
from ml.preprocessing.preprocess import run as preprocess_run  # noqa: E402
from ml.training.common import estimator_params, train_and_save  # noqa: E402
from ml.training.train_rf import build_estimator as build_rf  # noqa: E402
from ml.training.train_xgboost import build_estimator as build_xgb  # noqa: E402
from ml.utils.artifacts import git_commit, utc_now_iso, write_json  # noqa: E402
from ml.utils.config import load_config  # noqa: E402
from ml.utils.logging import get_logger  # noqa: E402

# alias -> (artifact name, estimator builder)
MODEL_REGISTRY = {
    "baseline": ("baseline", make_baseline),
    "rf": ("random_forest", build_rf),
    "xgb": ("xgboost", build_xgb),
}
TREE_MODELS = {"random_forest", "xgboost"}
VERSION = "0.1.0"


def _short_sha() -> str:
    sha = git_commit()
    return sha[:7] if sha else "nogit"


def _make_run_dir(config) -> Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(config.paths.artifacts_dir) / "runs" / f"{ts}_{_short_sha()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _attach_file_log(logger: logging.Logger, run_dir: Path) -> logging.Handler:
    handler = logging.FileHandler(run_dir / "run.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    return handler


def _format_summary(config, results: dict) -> str:
    header = f"{'model':16}{'macro-F1':>10}{'recall':>10}{'AUC':>10}{'accuracy':>11}"
    lines = ["", f"=== SUMMARY  dataset={config.name}  kind={config.kind}  seed={config.random_state} ===",
             header, "-" * len(header)]
    for name, m in results.items():
        auc = m["roc_auc_ovr_macro"]
        auc_str = f"{auc:.4f}" if auc is not None else "n/a"
        lines.append(f"{name:16}{m['f1_macro']:>10.4f}{m['recall_macro']:>10.4f}{auc_str:>10}{m['accuracy']:>11.4f}")
    return "\n".join(lines)


def run(config_path: str, model_arg: str) -> Path:
    config = load_config(config_path)

    run_dir = _make_run_dir(config)
    # Route ALL outputs into the run directory (self-contained, reproducible).
    config.paths.processed_dir = run_dir / "processed"
    config.paths.artifacts_dir = run_dir

    logger = get_logger()
    file_handler = _attach_file_log(logger, run_dir)
    try:
        logger.info("=== mbere-ml run: dataset=%s kind=%s models=%s seed=%s ===",
                    config.name, config.kind, model_arg, config.random_state)
        logger.info("run dir: %s", run_dir)

        # Snapshot the resolved config + a verbatim copy of the source YAML.
        write_json(json.loads(json.dumps(dataclasses.asdict(config), default=str)),
                   run_dir / "resolved_config.json")
        (run_dir / "config.yaml").write_text(Path(config_path).read_text(encoding="utf-8"), encoding="utf-8")

        # 1) preprocess once (load -> clean -> engineer -> split -> encode -> save)
        preprocess_run(config)

        # 2-4) per model: train (SMOTE in CV) -> evaluate -> SHAP (tree models)
        aliases = ["baseline", "rf", "xgb"] if model_arg == "all" else [model_arg]
        results: dict[str, dict] = {}
        for alias in aliases:
            name, builder = MODEL_REGISTRY[alias]
            estimator = builder(config)
            train_and_save(config, name, VERSION, estimator, estimator_params(estimator))
            results[name] = evaluate_model(config, name)
            if name in TREE_MODELS:
                try:
                    from ml.explainability.shap_analysis import analyze
                    analyze(config, name)
                except Exception as exc:  # SHAP is best-effort; never fail the run
                    logger.warning("SHAP failed for %s: %s", name, exc)

        # 5) comparison summary
        summary = {
            "dataset": config.name, "kind": config.kind, "random_state": config.random_state,
            "git_commit": git_commit(), "created_utc": utc_now_iso(),
            "models": {
                name: {k: m[k] for k in ("f1_macro", "recall_macro", "roc_auc_ovr_macro", "accuracy")}
                for name, m in results.items()
            },
        }
        write_json(summary, run_dir / "summary.json")

        table = _format_summary(config, results)
        print(table)
        for line in table.splitlines():
            logger.info(line)
        logger.info("run complete: %s", run_dir)
        return run_dir
    finally:
        logger.removeHandler(file_handler)
        file_handler.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible mbere-ml training run.")
    parser.add_argument("--config", required=True, help="Path to a dataset YAML config.")
    parser.add_argument("--model", default="all", choices=["rf", "xgb", "baseline", "all"])
    args = parser.parse_args()
    run(args.config, args.model)


if __name__ == "__main__":
    main()
