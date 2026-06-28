---
name: phase1b-modelling-results
description: Phase 1B baseline/RF/XGBoost results on Addis — weak feature signal, RF best, accuracy is a trap here
metadata:
  type: project
---

First modelling pass (Phase 1B) on the Addis severity target (5-fold CV, SMOTE-in-pipeline, held-out test). The honest finding: **the interpretable features carry weak signal for severity** (consistent with Phase 1A mutual-info scores of ~0.001–0.003).

Test-set headline metrics (the comparable `metrics.json` per model):
- **random_forest** — f1_macro 0.344, recall_macro 0.344, **roc_auc_ovr 0.567**, acc 0.726. The ONLY model with any Fatal recall (0.032).
- baseline (rule-based) — f1_macro 0.336, roc_auc 0.531, acc 0.765, Fatal recall 0.0.
- xgboost — f1_macro 0.330, roc_auc 0.530, acc 0.757, Fatal recall 0.0.

**Why this matters:** baseline/XGBoost get HIGHER accuracy by collapsing to the majority "Slight" class (the imbalance/accuracy trap — exactly why accuracy is banned as headline). RF trades accuracy for better minority recall + ROC-AUC, so RF is the current best and the only one detecting the rare Fatal class. SHAP top features: driver_experience, driver_age_band, time_of_day (matches the proposal's risk hypotheses).

**How to apply:** RF marginally beats the transparent baseline — don't oversell predictive power; the contribution is the leak-free, interpretable, reproducible pipeline. To improve: tune XGBoost (scale_pos_weight / class focus), try richer features (re-introduce dropped non-leakage columns, cyclical hour), or report calibrated risk bands rather than hard severity classes. See [[data-git-hygiene]] and [[python-env-313]].
