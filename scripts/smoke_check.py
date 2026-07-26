#!/usr/bin/env python
"""End-to-end smoke check against a HOSTED (or local) mbere-ml backend + frontend.

Exercises the same golden path as the manual "definition of done" in
frontend/README.md, but as a scriptable, repeatable check you can run after
every deploy: health -> register/login -> model contract -> predict -> models
catalog gate status -> frontend reachability.

Usage:
    python scripts/smoke_check.py --api https://mbere-ml.onrender.com \
        --frontend https://mbere-ml.netlify.app

Exits non-zero on the first failed check, printing which step failed and why.
This script makes real network calls -- run it from a machine/CI runner with
outbound internet access to the target host.
"""
from __future__ import annotations

import argparse
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import json as jsonlib


def _request(method: str, url: str, *, json: dict | None = None,
             form: dict | None = None, token: str | None = None,
             timeout: float = 30.0) -> tuple[int, dict | str]:
    data: bytes | None = None
    headers = {}
    if json is not None:
        data = jsonlib.dumps(json).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        status = exc.code
    try:
        parsed = jsonlib.loads(body) if body else {}
    except ValueError:
        parsed = body
    return status, parsed


def check(label: str, condition: bool, detail: str = "") -> None:
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {label}{f' -- {detail}' if detail and not condition else ''}")
    if not condition:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True, help="Backend base URL, e.g. https://mbere-ml.onrender.com")
    parser.add_argument("--frontend", default=None, help="Frontend base URL, e.g. https://mbere-ml.netlify.app")
    args = parser.parse_args()
    api = args.api.rstrip("/")

    # 1. Health
    status, body = _request("GET", f"{api}/health")
    check("GET /health reachable", status == 200, f"status={status} body={body}")
    check("model loaded", isinstance(body, dict) and body.get("model_loaded") is True, str(body))
    check("database ok", isinstance(body, dict) and body.get("db_ok") is True, str(body))
    print(f"    active model: {body.get('model')}")

    # 2. Register a throwaway user, then log in (proves the auth path end to end)
    email = f"smoke+{secrets.token_hex(4)}@example.test"
    password = "SmokeCheck!2026"
    status, body = _request(
        "POST", f"{api}/auth/register",
        json={"email": email, "password": password, "full_name": "Smoke Check"},
    )
    check("POST /auth/register", status in (200, 201), f"status={status} body={body}")

    status, body = _request(
        "POST", f"{api}/auth/token", form={"username": email, "password": password},
    )
    check("POST /auth/token", status == 200, f"status={status} body={body}")
    token = body["access_token"] if isinstance(body, dict) else None
    check("received JWT", bool(token))

    # 3. Feature contract for the active model
    status, body = _request("GET", f"{api}/models/contract", token=token)
    check("GET /models/contract", status == 200, f"status={status} body={body}")
    features = body.get("input_features", []) if isinstance(body, dict) else []
    check("contract has input features", len(features) > 0, str(body))

    # 4. Model catalog + decision-gate status
    status, body = _request("GET", f"{api}/models/catalog")
    check("GET /models/catalog", status == 200, f"status={status}")
    entries = body.get("models", []) if isinstance(body, dict) else []
    active = [m for m in entries if m.get("is_active")]
    check("exactly one active catalog model", len(active) == 1, str(active))
    if active:
        gate = active[0].get("gate_passed")
        print(f"    active model '{active[0]['name']}' gate_passed={gate}")
        check(
            "active model passes (or is exempt from) the deployment gate",
            gate is not False,
            f"reasons={active[0].get('gate_reasons')}",
        )

    # 5. A prediction using the contract's default-shaped values (first category
    #    per categorical feature, 0 for numeric) -- proves inference + SHAP + the
    #    audit-trail DB write all work end to end against the hosted DB.
    sample = {}
    for f in features:
        if f.get("kind") == "numeric":
            sample[f["name"]] = 0
        else:
            cats = f.get("categories") or ["Unknown"]
            sample[f["name"]] = cats[0]
    status, body = _request("POST", f"{api}/predict", json={"features": sample}, token=token)
    check("POST /predict", status == 200, f"status={status} body={body}")
    check("prediction has a risk band", isinstance(body, dict) and "risk_band" in body, str(body))
    check("prediction has a SHAP explanation", isinstance(body, dict) and body.get("explanation"), str(body))

    # 6. Frontend reachability (static asset, not a backend proxy check)
    if args.frontend:
        status, _ = _request("GET", args.frontend.rstrip("/") + "/")
        check("frontend reachable", status == 200, f"status={status}")

    print("\nAll smoke checks passed.")


if __name__ == "__main__":
    main()
