---
name: data-git-hygiene
description: Two repo hygiene quirks — autocrlf makes the raw CSVs show as fully modified, and a stray cleaned.csv sits in data/raw
metadata:
  type: project
---

Two things to know about the data/git state (neither caused by our code):

1. **`core.autocrlf=true`** makes the committed CSVs (`data/raw/RTA Dataset.csv`, `data/raw/cleaned.csv`) show as "modified" with every line changed (12317 insert / 12317 delete) — pure CRLF↔LF noise, not real edits. Consider a `.gitattributes` marking `*.csv` as `-text` (binary) or `text eol=lf` to stop the churn, and committing large CSVs is questionable anyway.

2. **`data/raw/cleaned.csv` is a stray pre-existing artifact** of unknown provenance. Per the data contract, cleaned/transformed data belongs in `data/processed/` (gitignored), and `RTA Dataset.csv` is the immutable source of truth. The reproducible pipeline regenerates processed sets from raw via `python -m ml.preprocessing.preprocess --config ml/configs/addis.yaml` (writes `data/processed/addis_{train,test}.csv` + encoded `.npz`, and `ml/artifacts/{encoders.joblib,feature_contract.json,split_indices.json}`). Treat `data/raw/cleaned.csv` as suspect; don't build on it. User has not yet decided whether to delete it. See [[python-env-313]].
