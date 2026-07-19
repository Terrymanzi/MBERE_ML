"""Inference service: load a versioned ML artifact and serve predictions.

This module ONLY deserializes artifacts produced by the `ml/` package and runs
them. It never fits/trains anything. The persisted artifact is a (imblearn or
sklearn) Pipeline ``encoder -> [smote] -> classifier``; at inference the sampler
is a no-op and the encoder transforms the raw feature row, so the backend feeds
RAW engineered features (exactly the contract's ``input_features``) and the
pipeline encodes internally.

Exception: XGBoost models. `XGBClassifier.__setstate__` hands its C++ core an
opaque bytearray during unpickling, and that framing is not guaranteed portable
across platforms -- trained on Colab/Linux, served here on Windows, joblib.load()
throws `XGBoostError: input stream corrupted` *inside* pickle's own unpickling,
before any object is returned. For any model with a `{name}_booster.ubj` +
`{name}_encoder.joblib` side-car pair sitting next to `{name}.pkl`,
`_load_xgboost_safe()` reconstructs the inference pipeline from those portable
parts instead of unpickling the `.pkl` directly. Every other model (RandomForest,
the rule-based baseline, etc.) is untouched and still goes through the plain
`load_pickle(model_path)` path.

Startup contract guarantee: the feature set the loaded model expects must match
the feature contract; otherwise loading fails fast (ContractMismatchError).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline as SkPipeline
from xgboost import XGBClassifier

from ..app.config import PROJECT_ROOT, Settings, get_settings
from ..utils_artifacts import load_pickle  # local thin joblib wrapper (see below)

logger = logging.getLogger("backend.model_service")

_TREE_CLASSIFIERS = {
    "RandomForestClassifier",
    "XGBClassifier",
    "ExtraTreesClassifier",
    "GradientBoostingClassifier",
    "LGBMClassifier",
    "DecisionTreeClassifier",
}


class ArtifactNotFoundError(RuntimeError):
    """No servable artifact found (degraded startup, not a hard failure)."""


class ContractMismatchError(RuntimeError):
    """Loaded model disagrees with its feature contract: fail fast."""


class FeatureValidationError(ValueError):
    """Submitted features don't satisfy the contract (-> HTTP 422)."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass
class PredictionResult:
    predicted_class: str
    predicted_index: int
    risk_band: str
    risk_score: float
    probabilities: dict[str, float]
    explanation: dict[str, Any]


@dataclass
class _Contract:
    dataset: str
    kind: str
    target_column: str
    classes: list[str]
    feature_names: list[str]
    features: list[dict] = field(default_factory=list)
    git_commit: str | None = None


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()


def _unwrap(model) -> tuple[Any, Any]:
    """Return (encoder_or_None, classifier) from a Pipeline-or-bare estimator."""
    if hasattr(model, "named_steps"):
        steps = model.named_steps
        classifier = steps.get("classifier") or list(steps.values())[-1]
        return steps.get("encoder"), classifier
    return None, model


def _load_xgboost_safe(run_dir: Path, name: str):
    """Reconstruct an XGBoost inference pipeline from side-car artifacts instead of the
    pickled Pipeline, when `{name}_booster.ubj` is present.

    XGBClassifier.__setstate__ hands its C++ core an opaque bytearray during unpickling,
    which is not guaranteed portable across platforms (trained on Colab/Linux, served here
    on Windows) -- joblib.load() throws `XGBoostError: input stream corrupted` *inside*
    pickle's own unpickling, before any object is returned, so there's nothing to repair
    after the fact. Instead the pipeline is rebuilt from parts each saved in a portable
    format: the encoder via plain joblib (numpy/sklearn only, no native blob), and the
    booster via XGBoost's own save_model/load_model (the documented portable format).

    classes_/n_classes_ are read-only properties on XGBClassifier (derived from the
    booster's own restored config, not stored as plain state) -- nothing to set here.
    `_aligned_proba()` already falls back to `np.arange(len(raw))` if `classes_` is
    unavailable, which is correct for this project since the target is always
    integer-encoded 0..n_classes-1 before fitting, and `predict_proba`'s output width
    comes from the booster's own restored `num_class` config, not from any sklearn-wrapper
    attribute.

    The sampler step is intentionally omitted: imblearn Pipelines skip sampler steps during
    .predict()/.transform() (resampling is training-only), so it's a no-op at inference --
    matching this module's own docstring -- and isn't needed for correct predictions.

    Returns None (caller falls back to the plain pickle) if no side-car export exists for
    this model name.
    """
    booster_path = run_dir / f"{name}_booster.ubj"
    if not booster_path.exists():
        return None

    encoder_path = run_dir / f"{name}_encoder.joblib"
    if not encoder_path.exists():
        raise ArtifactNotFoundError(
            f"found {booster_path.name} but not {encoder_path.name} -- re-run the Colab "
            f"export cell to also dump the encoder: joblib.dump(pipe.named_steps['encoder'], "
            f"artifacts_dir / '{name}_encoder.joblib')"
        )

    encoder = joblib.load(encoder_path)

    classifier = XGBClassifier()
    classifier.load_model(booster_path)

    logger.info("model %s: reconstructed from side-car encoder + booster (pickle bypassed)", name)
    return SkPipeline([("encoder", encoder), ("classifier", classifier)])


def _expected_features(model) -> list[str] | None:
    """Feature columns the model was fit on, if discoverable."""
    encoder, classifier = _unwrap(model)
    for obj in (encoder, model, classifier):
        names = getattr(obj, "feature_names_in_", None)
        if names is not None:
            return [str(n) for n in names]
    return None


def _category_caster(categories: list[Any] | None):
    """Pick a coercion fn so request values match how the encoder saw them
    (e.g. Porto ``_cat`` columns are ints, Addis categories are strings)."""
    cats = categories or []
    if cats and all(isinstance(c, bool) is False and isinstance(c, int) for c in cats):
        return lambda v: int(float(v))
    if cats and all(isinstance(c, (int, float)) and not isinstance(c, bool) for c in cats):
        return lambda v: float(v)
    return str


class ModelService:
    def __init__(self) -> None:
        self._loaded = False
        self._model = None
        self._encoder = None
        self._classifier = None
        self._explainer = None
        self._contract: _Contract | None = None
        self._meta: dict = {}
        self._run_dir: Path | None = None
        self._settings: Settings | None = None
        self._casters: dict[str, Any] = {}

    # --- lifecycle ----------------------------------------------------------
    def load(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        run_dir = self._select_run_dir()
        name = self._settings.model_name

        contract_path = run_dir / "feature_contract.json"
        model_path = run_dir / f"{name}.pkl"
        meta_path = run_dir / f"{name}.meta.json"
        for p in (contract_path, model_path):
            if not p.exists():
                raise ArtifactNotFoundError(f"missing artifact file: {p}")

        contract_raw = json.loads(contract_path.read_text(encoding="utf-8"))
        contract = _Contract(
            dataset=contract_raw["dataset"],
            kind=contract_raw["kind"],
            target_column=contract_raw["target"]["column"],
            classes=list(contract_raw["target"]["classes"]),
            feature_names=[f["name"] for f in contract_raw["input_features"]],
            features=contract_raw["input_features"],
            git_commit=contract_raw.get("git_commit"),
        )
        model = _load_xgboost_safe(run_dir, name) or load_pickle(model_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

        self._validate(model, contract, meta)

        self._model = model
        self._encoder, self._classifier = _unwrap(model)
        self._contract = contract
        self._meta = meta
        self._run_dir = run_dir
        self._explainer = None  # built lazily on first explanation
        self._casters = {
            f["name"]: _category_caster(f.get("categories"))
            for f in contract.features
            if f.get("kind") == "categorical"
        }
        self._loaded = True
        logger.info(
            "model loaded: %s v%s dataset=%s kind=%s from %s",
            name, self.version, contract.dataset, contract.kind, run_dir,
        )

    def _select_run_dir(self) -> Path:
        if self._settings.model_run_dir:
            run_dir = _resolve(self._settings.model_run_dir)
            if not run_dir.exists():
                raise ArtifactNotFoundError(f"model_run_dir does not exist: {run_dir}")
            return run_dir
        root = _resolve(self._settings.artifacts_root)
        name = self._settings.model_name
        if not root.exists():
            raise ArtifactNotFoundError(f"artifacts_root does not exist: {root}")
        candidates = sorted(
            (d for d in root.iterdir()
             if d.is_dir()
             and (d / f"{name}.pkl").exists()
             and (d / "feature_contract.json").exists()),
            key=lambda d: d.name,
        )
        if not candidates:
            raise ArtifactNotFoundError(
                f"no run under {root} contains {name}.pkl + feature_contract.json"
            )
        return candidates[-1]  # latest by timestamped dir name

    def _validate(self, model, contract: _Contract, meta: dict) -> None:
        if not contract.feature_names:
            raise ContractMismatchError("contract lists no input features")
        if not contract.classes:
            raise ContractMismatchError("contract lists no target classes")

        expected = _expected_features(model)
        if expected is not None and set(expected) != set(contract.feature_names):
            missing = sorted(set(expected) - set(contract.feature_names))
            extra = sorted(set(contract.feature_names) - set(expected))
            raise ContractMismatchError(
                "model/contract feature mismatch — "
                f"model_only={missing} contract_only={extra}"
            )
        meta_classes = (meta.get("dataset") or {}).get("classes")
        if meta_classes and list(meta_classes) != contract.classes:
            raise ContractMismatchError(
                f"class order differs: meta={meta_classes} contract={contract.classes}"
            )

    # --- introspection ------------------------------------------------------
    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def name(self) -> str:
        return self._settings.model_name if self._settings else ""

    @property
    def version(self) -> str:
        return str(self._meta.get("model_version", "unknown"))

    @property
    def contract(self) -> _Contract:
        self._require()
        return self._contract

    @property
    def feature_names(self) -> list[str]:
        return self.contract.feature_names

    @property
    def classes(self) -> list[str]:
        return self.contract.classes

    @property
    def run_dir(self) -> Path:
        self._require()
        return self._run_dir

    def model_info(self) -> dict:
        self._require()
        return {
            "name": self.name,
            "version": self.version,
            "dataset": self._contract.dataset,
            "kind": self._contract.kind,
            "classes": self._contract.classes,
        }

    def identity(self) -> dict:
        """Registry identity for the served artifact (-> ModelVersion row)."""
        self._require()
        return {
            "name": self.name,
            "version": self.version,
            "dataset_name": self._contract.dataset,
            "kind": self._contract.kind,
            "target_classes": self._contract.classes,
            "run_dir": str(self._run_dir),
            "git_commit": self._contract.git_commit or self._meta.get("git_commit"),
            "metrics": self._meta.get("metrics_cv", {}) or {},
        }

    def _require(self) -> None:
        if not self._loaded:
            raise ArtifactNotFoundError("model is not loaded")

    # --- validation + inference --------------------------------------------
    def validate_features(self, features: dict[str, Any]) -> dict[str, Any]:
        """Validate/coerce a raw feature map against the contract.

        Returns a dict ordered like the contract; raises FeatureValidationError.
        """
        self._require()
        errors: list[str] = []
        provided = set(features)
        required = set(self.feature_names)
        missing = sorted(required - provided)
        unknown = sorted(provided - required)
        if missing:
            errors.append(f"missing required features: {missing}")
        if unknown:
            errors.append(f"unknown features (not in contract): {unknown}")

        coerced: dict[str, Any] = {}
        for spec in self._contract.features:
            name = spec["name"]
            if name not in features:
                continue
            value = features[name]
            if value is None:
                errors.append(f"{name}: null not allowed")
                continue
            if spec.get("kind") == "numeric" or spec.get("encoding") == "numeric":
                try:
                    coerced[name] = float(value)
                except (TypeError, ValueError):
                    errors.append(f"{name}: expected a number, got {value!r}")
            else:  # categorical
                try:
                    coerced[name] = self._casters[name](value)
                except (TypeError, ValueError):
                    coerced[name] = str(value)

        if errors:
            raise FeatureValidationError(errors)
        return {n: coerced[n] for n in self.feature_names}

    def predict(self, features: dict[str, Any]) -> PredictionResult:
        self._require()
        coerced = self.validate_features(features)
        X = pd.DataFrame([coerced], columns=self.feature_names)

        proba = self._aligned_proba(X)
        pred_index = int(np.argmax(proba))
        predicted_class = self.classes[pred_index]
        risk_score = self._risk_score(proba)
        risk_band = self._band(risk_score)
        probabilities = {self.classes[i]: float(proba[i]) for i in range(len(self.classes))}
        explanation = self._explain(X, coerced, pred_index)

        return PredictionResult(
            predicted_class=predicted_class,
            predicted_index=pred_index,
            risk_band=risk_band,
            risk_score=float(risk_score),
            probabilities=probabilities,
            explanation=explanation,
        )

    def _aligned_proba(self, X: pd.DataFrame) -> np.ndarray:
        raw = np.asarray(self._model.predict_proba(X))[0]
        n = len(self.classes)
        classes_ = getattr(self._model, "classes_", np.arange(len(raw)))
        out = np.zeros(n, dtype=float)
        for pos, code in enumerate(classes_):
            idx = int(code)
            if 0 <= idx < n:
                out[idx] = raw[pos]
        s = out.sum()
        return out / s if s > 0 else out

    def _risk_score(self, proba: np.ndarray) -> float:
        n = len(proba)
        if n <= 2:                       # binary: P(positive / "claim")
            return float(proba[-1])
        # multiclass severity: normalized expected severity index in [0,1]
        return float(sum(i * p for i, p in enumerate(proba)) / (n - 1))

    def _band(self, score: float) -> str:
        s = self._settings
        if score < s.risk_band_low_max:
            return "Low"
        if score < s.risk_band_medium_max:
            return "Medium"
        return "High"

    # --- explanation --------------------------------------------------------
    def _explain(self, X: pd.DataFrame, coerced: dict, pred_index: int) -> dict:
        try:
            if self._encoder is not None:
                X_enc = np.asarray(self._encoder.transform(X))
                enc_names = list(self._encoder.get_feature_names_out())
            else:
                X_enc = X.to_numpy(dtype=float)
                enc_names = list(X.columns)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("explain: encoding failed (%s)", exc)
            return {"method": "none", "base_value": None, "top_features": []}

        method, contributions, base_value = self._contributions(X_enc, enc_names, pred_index)
        if contributions is None:
            return {"method": "none", "base_value": None, "top_features": []}

        agg = self._aggregate(enc_names, contributions, coerced)
        top_k = self._settings.explain_top_k
        agg.sort(key=lambda d: d["abs_contribution"], reverse=True)
        return {"method": method, "base_value": base_value, "top_features": agg[:top_k]}

    def _contributions(self, X_enc, enc_names, pred_index):
        """Return (method, per-encoded-feature contribution vector, base_value)."""
        clf = self._classifier
        clf_name = type(clf).__name__
        # 1) SHAP for tree models
        if clf_name in _TREE_CLASSIFIERS:
            try:
                import shap

                if self._explainer is None:
                    self._explainer = shap.TreeExplainer(clf)
                expl = self._explainer(X_enc, check_additivity=False)
                values = np.asarray(expl.values)
                base = np.asarray(expl.base_values)
                if values.ndim == 3:               # (n, f, c)
                    col = pred_index if pred_index < values.shape[2] else values.shape[2] - 1
                    row = values[0, :, col]
                    base_value = float(np.ravel(base)[col]) if base.size > 1 else float(base.ravel()[0])
                else:                               # (n, f) single output
                    row = values[0]
                    base_value = float(np.ravel(base)[0])
                return "shap", np.asarray(row, dtype=float), base_value
            except Exception as exc:
                logger.warning("explain: SHAP failed (%s); falling back", exc)

        # 2) linear models: signed coef * encoded value
        coef = getattr(clf, "coef_", None)
        if coef is not None:
            coef = np.asarray(coef)
            if coef.ndim == 2 and coef.shape[0] > 1:
                w = coef[pred_index]
            elif coef.ndim == 2:
                w = coef[0] * (1.0 if pred_index == 1 else -1.0)
            else:
                w = coef * (1.0 if pred_index == 1 else -1.0)
            return "linear", np.asarray(w, dtype=float) * np.asarray(X_enc[0], dtype=float), None

        return "none", None, None

    def _aggregate(self, enc_names, contributions, coerced) -> list[dict]:
        """Sum encoded contributions back onto their source input features."""
        sums: dict[str, float] = {f: 0.0 for f in self.feature_names}
        for enc_name, contrib in zip(enc_names, contributions):
            src = self._source_feature(enc_name)
            sums[src] = sums.get(src, 0.0) + float(contrib)
        out = []
        for feat, total in sums.items():
            out.append({
                "feature": feat,
                "value": coerced.get(feat),
                "contribution": float(total),
                "abs_contribution": abs(float(total)),
            })
        return out

    def _source_feature(self, enc_name: str) -> str:
        body = enc_name.split("__", 1)[1] if "__" in enc_name else enc_name
        candidates = [f for f in self.feature_names if body == f or body.startswith(f + "_")]
        return max(candidates, key=len) if candidates else body