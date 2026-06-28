"""/health and basic readiness."""
from __future__ import annotations


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db_ok"] is True
    assert body["model_loaded"] is True
    assert body["model"]["kind"] == "multiclass"
    assert body["n_input_features"] == 3


def test_openapi_docs_served(client):
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_models_registry_has_active(client):
    r = client.get("/models")
    assert r.status_code == 200
    versions = r.json()
    assert len(versions) >= 1
    active = [v for v in versions if v["is_active"]]
    assert len(active) == 1
    assert active[0]["name"] == "random_forest"


def test_active_contract(client):
    r = client.get("/models/contract")
    assert r.status_code == 200
    body = r.json()
    names = [f["name"] for f in body["input_features"]]
    assert names == ["vehicle_type", "driver_age", "driver_experience"]
