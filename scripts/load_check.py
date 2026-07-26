#!/usr/bin/env python
"""Lightweight concurrency/latency probe for the /predict endpoint.

Not a substitute for a real load-testing tool (k6, Locust) at scale, but
dependency-free (stdlib `concurrent.futures` + `urllib`) so it can be run
against any environment -- a laptop, a CI runner, or the hosted Render
instance -- to get a real, reproducible p50/p95/p99 latency reading and a
pass/fail count under N concurrent requests. Intended to be re-run per
hardware/software environment and the results recorded in the README's test
matrix, rather than asserting untested numbers.

Usage:
    python scripts/load_check.py --api http://localhost:8000 --requests 50 --concurrency 10
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request


def _register_and_login(api: str) -> str:
    import secrets

    email = f"loadcheck+{secrets.token_hex(4)}@example.test"
    password = "LoadCheck!2026"
    req = urllib.request.Request(
        f"{api}/auth/register",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=30)

    req = urllib.request.Request(
        f"{api}/auth/token",
        data=urllib.parse.urlencode({"username": email, "password": password}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def _sample_features(api: str, token: str) -> dict:
    req = urllib.request.Request(
        f"{api}/models/contract", headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        contract = json.loads(resp.read())
    sample = {}
    for f in contract["input_features"]:
        if f.get("kind") == "numeric":
            sample[f["name"]] = 0
        else:
            sample[f["name"]] = (f.get("categories") or ["Unknown"])[0]
    return sample


def _one_predict(api: str, token: str, features: dict) -> tuple[bool, float]:
    body = json.dumps({"features": features}).encode()
    req = urllib.request.Request(
        f"{api}/predict",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            ok = resp.status == 200
    except urllib.error.HTTPError:
        ok = False
    elapsed_ms = (time.perf_counter() - start) * 1000
    return ok, elapsed_ms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", required=True)
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    api = args.api.rstrip("/")

    token = _register_and_login(api)
    features = _sample_features(api, token)

    latencies: list[float] = []
    failures = 0
    start = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [
            pool.submit(_one_predict, api, token, features) for _ in range(args.requests)
        ]
        for fut in cf.as_completed(futures):
            ok, ms = fut.result()
            latencies.append(ms)
            if not ok:
                failures += 1
    total_s = time.perf_counter() - start

    latencies.sort()

    def pct(p: float) -> float:
        idx = min(len(latencies) - 1, int(len(latencies) * p))
        return latencies[idx]

    print(f"requests={args.requests} concurrency={args.concurrency} failures={failures}")
    print(f"wall_time={total_s:.2f}s throughput={args.requests / total_s:.1f} req/s")
    print(
        f"latency_ms: min={min(latencies):.0f} p50={pct(0.50):.0f} "
        f"p95={pct(0.95):.0f} p99={pct(0.99):.0f} max={max(latencies):.0f} "
        f"mean={statistics.mean(latencies):.0f}"
    )
    if failures:
        raise SystemExit(f"{failures}/{args.requests} requests failed")


if __name__ == "__main__":
    main()
