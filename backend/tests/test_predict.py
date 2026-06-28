"""/predict: happy path, explanation, persistence, and bad-feature rejection."""
from __future__ import annotations

import uuid


def test_predict_happy_path(client, auth_headers, valid_features):
    r = client.post("/predict", json={"features": valid_features}, headers=auth_headers)
    assert r.status_code == 200, r.text
    body = r.json()

    # risk band + probabilities
    assert body["risk_band"] in {"Low", "Medium", "High"}
    assert 0.0 <= body["risk_score"] <= 1.0
    probs = body["probabilities"]
    assert set(probs) == {"Slight Injury", "Serious Injury", "Fatal Injury"}
    assert abs(sum(probs.values()) - 1.0) < 1e-6
    assert body["predicted_class"] in probs

    # explanation (SHAP for the tree model), mapped back to ORIGINAL features
    expl = body["explanation"]
    assert expl["method"] == "shap"
    assert len(expl["top_features"]) >= 1
    contract_feats = {"vehicle_type", "driver_age", "driver_experience"}
    assert all(f["feature"] in contract_feats for f in expl["top_features"])

    # an audit trail was created
    assert body["risk_assessment_id"] > 0
    assert body["prediction_id"] > 0
    assert body["model"]["version"] == "0.1.0-test"


def test_predict_persists_and_links_to_driver(client, auth_headers, valid_features):
    lic = f"RW-{uuid.uuid4().hex[:8]}"
    drv = client.post(
        "/drivers",
        json={"license_number": lic, "full_name": "Jean P."},
        headers=auth_headers,
    )
    assert drv.status_code == 201, drv.text
    driver_id = drv.json()["id"]

    pred = client.post(
        "/predict",
        json={"driver_id": driver_id, "features": valid_features},
        headers=auth_headers,
    )
    assert pred.status_code == 200, pred.text

    hist = client.get(f"/risk/{driver_id}", headers=auth_headers)
    assert hist.status_code == 200
    rows = hist.json()
    assert len(rows) == 1
    assert rows[0]["prediction"]["predicted_class"] == pred.json()["predicted_class"]
    assert rows[0]["prediction"]["model_version_id"] >= 1  # audit FK present


def test_predict_unknown_driver_404(client, auth_headers, valid_features):
    r = client.post(
        "/predict",
        json={"driver_id": 999999, "features": valid_features},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_predict_missing_feature_rejected(client, auth_headers):
    bad = {"vehicle_type": "Motorcycle", "driver_age": 19}  # missing driver_experience
    r = client.post("/predict", json={"features": bad}, headers=auth_headers)
    assert r.status_code == 422
    assert "driver_experience" in str(r.json()["detail"])


def test_predict_bad_type_rejected(client, auth_headers):
    bad = {"vehicle_type": "Motorcycle", "driver_age": "not-a-number", "driver_experience": 1}
    r = client.post("/predict", json={"features": bad}, headers=auth_headers)
    assert r.status_code == 422


def test_predict_unknown_feature_rejected(client, auth_headers, valid_features):
    payload = dict(valid_features, surprise_feature=1)
    r = client.post("/predict", json={"features": payload}, headers=auth_headers)
    assert r.status_code == 422
    assert "surprise_feature" in str(r.json()["detail"])
