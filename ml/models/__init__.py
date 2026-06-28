"""Models for the mbere-ml package."""
from __future__ import annotations

from .baseline import RuleBasedRiskClassifier

__all__ = ["RuleBasedRiskClassifier", "make_baseline"]


def make_baseline(config):
    """Config-selected transparent baseline.

      * "rule_based" -> RuleBasedRiskClassifier (Addis interpretable rules)
      * "logistic"   -> encoder -> LogisticRegression (generic/binary; class_weight
                        balanced for imbalance). Transparent linear model, not a dummy.
    """
    kind = config.baseline.kind
    if kind == "rule_based":
        return RuleBasedRiskClassifier()
    if kind == "logistic":
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        from ..preprocessing.encode import build_encoder

        classifier = LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=config.random_state
        )
        return Pipeline([("encoder", build_encoder(config)), ("classifier", classifier)])
    raise ValueError(f"Unknown baseline kind: {kind!r} (expected 'rule_based' or 'logistic').")
