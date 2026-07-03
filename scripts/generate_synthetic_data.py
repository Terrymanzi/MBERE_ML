"""Generate and validate the synthetic Rwandan driver-risk dataset.

Loads the Fabricate-generated CSV, validates every category against the real
feature vocabulary, writes the validated rows to data/processed/rwanda_synthetic.csv,
and prints a sanity-check summary.

Usage:
    python scripts/generate_synthetic_data.py \\
        --fabricate-csv data/external/synthetic/rwanda_driver_risk_profiles_synthetic.csv \\
        --out data/processed/rwanda_synthetic.csv

Optional:
    --contract   path to feature_contract.json  (auto-detected from latest run if omitted)
    --model      path to model .pkl              (auto-detected from latest run if omitted)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.synthetic.generate import load_and_validate, sanity_check  # noqa: E402


def _latest_run_dir(artifacts_root: Path) -> Path:
    runs = sorted(
        (d for d in artifacts_root.iterdir() if d.is_dir()),
        key=lambda d: d.name,
    )
    if not runs:
        raise FileNotFoundError(f"No run directories found under {artifacts_root}")
    return runs[-1]


def _resolve_artifacts(contract_arg: str | None, model_arg: str | None) -> tuple[Path, Path]:
    artifacts_root = ROOT / "ml" / "artifacts" / "runs"
    run_dir = _latest_run_dir(artifacts_root)

    contract_path = Path(contract_arg) if contract_arg else run_dir / "feature_contract.json"
    model_path = Path(model_arg) if model_arg else run_dir / "xgboost.pkl"
    if not model_path.exists():
        model_path = run_dir / "random_forest.pkl"

    if not contract_path.exists():
        raise FileNotFoundError(f"feature_contract.json not found at {contract_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"No model .pkl found in {run_dir}")

    return contract_path, model_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and export synthetic Rwandan dataset.")
    parser.add_argument("--fabricate-csv", required=True, help="Path to Fabricate-generated CSV.")
    parser.add_argument("--out", default="data/processed/rwanda_synthetic.csv",
                        help="Output path for validated CSV.")
    parser.add_argument("--contract", default=None, help="Path to feature_contract.json.")
    parser.add_argument("--model", default=None, help="Path to model .pkl for sanity check.")
    args = parser.parse_args()

    fabricate_csv = Path(args.fabricate_csv)
    out_path = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)

    print(f"Loading: {fabricate_csv}")
    try:
        contract_path, model_path = _resolve_artifacts(args.contract, args.model)
        df = load_and_validate(fabricate_csv, contract_path)
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}")
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Written: {out_path}  ({len(df)} rows)")

    print("\nRunning contextual sanity check...")
    try:
        result = sanity_check(df, model_path, encoder_path=None, contract_path=contract_path)
        print(f"\n  {result['note']}")
        print(f"  Labels evaluated : {result['labels_evaluated']}")
        print(f"  Mean P(Fatal)    : {result['mean_p_fatal']}")
        print(f"  Mean P(Serious)  : {result['mean_p_serious']}")
        print(f"  Monotonic Fatal  : {result['monotonic_fatal']}")
        print(f"  Monotonic Serious: {result['monotonic_serious']}")
    except Exception as exc:
        print(f"  Sanity check skipped: {exc}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
