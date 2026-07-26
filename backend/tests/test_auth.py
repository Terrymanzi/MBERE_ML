"""Auth: registration, login, protected routes."""
from __future__ import annotations

import uuid


def _email() -> str:
    return f"auth-{uuid.uuid4().hex[:8]}@test.com"


def test_register_login_me(client):
    email, pw = _email(), "supersecret1"
    reg = client.post("/auth/register", json={"email": email, "password": pw})
    assert reg.status_code == 201
    assert reg.json()["email"] == email
    assert "hashed_password" not in reg.json()  # never leak the hash

    tok = client.post("/auth/token", data={"username": email, "password": pw})
    assert tok.status_code == 200
    token = tok.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_duplicate_registration_conflicts(client):
    email, pw = _email(), "supersecret1"
    assert client.post("/auth/register", json={"email": email, "password": pw}).status_code == 201
    dup = client.post("/auth/register", json={"email": email, "password": pw})
    assert dup.status_code == 409


def test_weak_password_rejected(client):
    r = client.post("/auth/register", json={"email": _email(), "password": "short"})
    assert r.status_code == 422


def test_wrong_password_unauthorized(client):
    email, pw = _email(), "supersecret1"
    client.post("/auth/register", json={"email": email, "password": pw})
    bad = client.post("/auth/token", data={"username": email, "password": "wrong-password"})
    assert bad.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_invalid_token_rejected(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-jwt"})
    assert r.status_code == 401


def test_predict_requires_auth(client, valid_features):
    assert client.post("/predict", json={"features": valid_features}).status_code == 401


def test_register_defaults_to_fleet_manager_and_rejects_admin(client):
    email, pw = _email(), "supersecret1"
    reg = client.post("/auth/register", json={"email": email, "password": pw})
    assert reg.status_code == 201
    assert reg.json()["role"] == "FLEET_MANAGER"

    rejected = client.post(
        "/auth/register", json={"email": _email(), "password": pw, "role": "ADMIN"}
    )
    assert rejected.status_code == 422


def test_login_returns_refresh_token_and_role_claim(client):
    from backend.auth.security import decode_access_token

    email, pw = _email(), "supersecret1"
    client.post("/auth/register", json={"email": email, "password": pw})
    tok = client.post("/auth/token", data={"username": email, "password": pw})
    assert tok.status_code == 200
    body = tok.json()
    assert body["refresh_token"]
    payload = decode_access_token(body["access_token"])
    assert payload["role"] == "FLEET_MANAGER"


def test_refresh_issues_new_access_token_and_rejects_access_token(client):
    email, pw = _email(), "supersecret1"
    client.post("/auth/register", json={"email": email, "password": pw})
    tok = client.post("/auth/token", data={"username": email, "password": pw}).json()

    refreshed = client.post("/auth/refresh", json={"refresh_token": tok["refresh_token"]})
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["access_token"]

    rejected = client.post("/auth/refresh", json={"refresh_token": tok["access_token"]})
    assert rejected.status_code == 401


def test_change_password_happy_path_and_wrong_current(client):
    email, pw = _email(), "supersecret1"
    client.post("/auth/register", json={"email": email, "password": pw})
    tok = client.post("/auth/token", data={"username": email, "password": pw}).json()
    headers = {"Authorization": f"Bearer {tok['access_token']}"}

    wrong = client.post(
        "/auth/change-password",
        json={"current_password": "not-it", "new_password": "newsecret1"},
        headers=headers,
    )
    assert wrong.status_code == 401

    ok = client.post(
        "/auth/change-password",
        json={"current_password": pw, "new_password": "newsecret1"},
        headers=headers,
    )
    assert ok.status_code == 204

    relogin = client.post("/auth/token", data={"username": email, "password": "newsecret1"})
    assert relogin.status_code == 200
