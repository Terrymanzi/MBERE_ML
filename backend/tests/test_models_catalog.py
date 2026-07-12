"""GET /models/catalog — disk-scanned catalog merged with DB active status."""
from __future__ import annotations


def test_catalog_lists_all_models_with_test_metrics(client):
    r = client.get("/models/catalog")
    assert r.status_code == 200
    body = r.json()
    names = {m["name"] for m in body["models"]}
    assert {"baseline", "random_forest"} <= names

    baseline = next(m for m in body["models"] if m["name"] == "baseline")
    assert baseline["metrics_test"] is not None
    assert baseline["metrics_test"]["accuracy"] == 0.8
    assert baseline["metrics_test"]["n_samples"] == 48

    # "random_forest" was seeded without a reports/*/metrics.json -> null, not an error.
    rf = next(m for m in body["models"] if m["name"] == "random_forest")
    assert rf["metrics_test"] is None
    assert rf["metrics_cv"]  # still has CV metrics from meta.json


def test_catalog_reflects_db_activation_status(client, auth_headers):
    r = client.post("/models/baseline/activate", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["is_active"] is True

    catalog = client.get("/models/catalog").json()["models"]
    active_entries = [m for m in catalog if m["is_active"]]
    assert [m["name"] for m in active_entries] == ["baseline"]
    baseline_entry = next(m for m in catalog if m["name"] == "baseline")
    assert baseline_entry["model_version_id"] is not None
