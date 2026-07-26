"""Deployment decision gate: is a candidate model fit to serve production traffic?

Per the capstone report's acceptance criterion (Table 8, Objective 2), a
machine-learning candidate is only production-eligible if it beats the transparent
rule-based baseline on ALL THREE held-out-test headline metrics: macro-F1,
macro-recall, and one-vs-rest macro ROC-AUC. Accuracy is deliberately excluded
(a model can hit ~85% accuracy by predicting the majority class alone).

Fatal-class recall is NOT a gate criterion: every candidate trained so far (baseline
included) recovers at most 2 of 31 held-out Fatal cases, so treating it as a hard
blocker would make the gate unsatisfiable by design rather than informative. Instead,
near-zero Fatal recall is surfaced as a disclosed limitation, and is why the served
risk score is framed as a crash-severity/profile-risk signal rather than a claim
about any individual driver's future outcome (see README "Reframing" section).
"""
from __future__ import annotations

from dataclasses import dataclass, field

HEADLINE_METRICS: tuple[str, ...] = ("f1_macro", "recall_macro", "roc_auc_ovr_macro")


@dataclass
class GateResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


def evaluate_gate(
    candidate_metrics: dict,
    baseline_metrics: dict,
    metrics: tuple[str, ...] = HEADLINE_METRICS,
) -> GateResult:
    """Compare a candidate's held-out test metrics against the baseline's.

    Both dicts are the contents of a ``reports/<name>/metrics.json`` file (or any
    dict exposing the same keys). The candidate must be >= the baseline on every
    metric in ``metrics``; missing/None values fail closed (treated as a loss).
    """
    reasons: list[str] = []
    for name in metrics:
        c, b = candidate_metrics.get(name), baseline_metrics.get(name)
        if c is None or b is None:
            reasons.append(f"{name}: missing on candidate or baseline")
            continue
        if c < b:
            reasons.append(f"{name}: {c:.4f} < baseline {b:.4f}")
    return GateResult(passed=not reasons, reasons=reasons)
