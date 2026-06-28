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
