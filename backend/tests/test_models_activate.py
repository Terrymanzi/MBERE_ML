"""POST /models/{name}/activate — org-wide active model switch."""
from __future__ import annotations


def test_activate_requires_auth(client):
    r = client.post("/models/baseline/activate")
    assert r.status_code == 401


def test_activate_unknown_model_404(client, auth_headers):
    r = client.post("/models/does-not-exist/activate", headers=auth_headers)
    assert r.status_code == 404


def test_activate_switches_default_used_by_predict(client, auth_headers, valid_features):
    r = client.post("/models/random_forest/activate", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "random_forest"
    assert r.json()["is_active"] is True

    pred = client.post("/predict", json={"features": valid_features}, headers=auth_headers)
    assert pred.status_code == 200, pred.text
    assert pred.json()["model"]["name"] == "random_forest"


def test_activate_allowed_for_any_authenticated_user(client, auth_headers):
    """No superuser gate: any authenticated user can change the org-wide default."""
    r = client.post("/models/baseline/activate", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["is_active"] is True
