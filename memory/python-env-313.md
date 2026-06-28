---
name: python-env-313
description: Dev machine only has Python 3.13.9, but mbere-ml targets 3.11; venv + library version gotchas
metadata:
  type: project
---

The stack contract says **Python 3.11**, but the only interpreter installed on this Windows machine is **3.13.9** (`py` launcher; no 3.11, no system venv). We proceed on a project-root **`.venv` built with 3.13** (gitignored). The user has NOT yet decided whether to install 3.11.

**Why:** Need to make progress; all libs support 3.13. But this deviates from the reproducibility contract, so artifacts/metadata should record the actual interpreter, and a 3.11 venv may be needed later for the official run.

**How to apply:**
- Run Python via `.\.venv\Scripts\python.exe`; run tests with `.\.venv\Scripts\python.exe -m pytest` from repo root (pytest config in root `pyproject.toml` sets `pythonpath=["."]` so `import ml...` works).
- Installed: pandas 3.0.3, numpy 2.5.0, scikit-learn 1.9.0, PyYAML 6.0.3, pytest 9.1.1 (pinned in [ml/requirements.txt]). Training deps (xgboost, imbalanced-learn, shap) not installed yet.
- **pandas 3.0 gotcha:** text columns load as the new `str` dtype, so `select_dtypes(include="object")` misses them and warns. Operate on explicit config-driven column lists instead (the preprocessing code already does this).
