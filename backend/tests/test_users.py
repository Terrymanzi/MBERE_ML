"""Admin-only user management + audit log."""
from __future__ import annotations

import uuid


def _email() -> str:
    return f"admin-mgmt-{uuid.uuid4().hex[:8]}@test.com"


def test_all_endpoints_forbidden_for_non_admin(client, auth_headers):
    assert client.get("/users", headers=auth_headers).status_code == 403
    assert client.post("/users", json={}, headers=auth_headers).status_code == 403
    assert client.put("/users/1", json={}, headers=auth_headers).status_code == 403
    assert client.delete("/users/1", headers=auth_headers).status_code == 403
    assert client.patch("/users/1/role", json={"role": "ADMIN"}, headers=auth_headers).status_code == 403
    assert client.patch("/users/1/active", json={"is_active": False}, headers=auth_headers).status_code == 403
    assert (
        client.post("/users/1/reset-password", json={"new_password": "newsecret1"}, headers=auth_headers).status_code
        == 403
    )
    assert client.get("/audit-logs", headers=auth_headers).status_code == 403


def test_create_list_update_user(client, admin_auth_headers):
    email = _email()
    created = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "INSURER", "full_name": "New Insurer"},
        headers=admin_auth_headers,
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["role"] == "INSURER"
    user_id = body["id"]

    dup = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "INSURER"},
        headers=admin_auth_headers,
    )
    assert dup.status_code == 409

    listed = client.get("/users", params={"q": "New Insurer"}, headers=admin_auth_headers)
    assert listed.status_code == 200
    assert any(u["id"] == user_id for u in listed.json())

    updated = client.put(
        f"/users/{user_id}", json={"full_name": "Renamed Insurer"}, headers=admin_auth_headers
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Renamed Insurer"


def test_role_and_active_toggle(client, admin_auth_headers):
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "FLEET_MANAGER"},
        headers=admin_auth_headers,
    ).json()["id"]

    role_resp = client.patch(f"/users/{user_id}/role", json={"role": "ADMIN"}, headers=admin_auth_headers)
    assert role_resp.status_code == 200
    assert role_resp.json()["role"] == "ADMIN"

    active_resp = client.patch(
        f"/users/{user_id}/active", json={"is_active": False}, headers=admin_auth_headers
    )
    assert active_resp.status_code == 200
    assert active_resp.json()["is_active"] is False


def test_admin_cannot_modify_or_delete_self(client, admin_auth_headers):
    me = client.get("/auth/me", headers=admin_auth_headers).json()
    admin_id = me["id"]

    assert (
        client.patch(f"/users/{admin_id}/role", json={"role": "INSURER"}, headers=admin_auth_headers).status_code
        == 400
    )
    assert (
        client.patch(f"/users/{admin_id}/active", json={"is_active": False}, headers=admin_auth_headers).status_code
        == 400
    )
    assert client.delete(f"/users/{admin_id}", headers=admin_auth_headers).status_code == 400


def test_reset_password_then_login_with_new_password(client, admin_auth_headers):
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "oldsecret1", "role": "FLEET_MANAGER"},
        headers=admin_auth_headers,
    ).json()["id"]

    reset = client.post(
        f"/users/{user_id}/reset-password",
        json={"new_password": "brandnewsecret1"},
        headers=admin_auth_headers,
    )
    assert reset.status_code == 204

    login = client.post("/auth/token", data={"username": email, "password": "brandnewsecret1"})
    assert login.status_code == 200


def test_delete_user_without_dependents(client, admin_auth_headers):
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "FLEET_MANAGER"},
        headers=admin_auth_headers,
    ).json()["id"]

    deleted = client.delete(f"/users/{user_id}", headers=admin_auth_headers)
    assert deleted.status_code == 204

    listed = client.get("/users", headers=admin_auth_headers).json()
    assert all(u["id"] != user_id for u in listed)


def test_delete_user_nulls_driver_attribution_instead_of_blocking(client, admin_auth_headers):
    """created_by_user_id is nullable with no cascade -- SQLAlchemy's default
    behavior un-attributes the record rather than blocking the delete. The
    driver itself is business data and should survive; only accountability
    (audit_logs, see below) is meant to actually block deletion."""
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "FLEET_MANAGER"},
        headers=admin_auth_headers,
    ).json()["id"]

    tok = client.post("/auth/token", data={"username": email, "password": "supersecret1"})
    owner_headers = {"Authorization": f"Bearer {tok.json()['access_token']}"}
    driver = client.post(
        "/drivers",
        json={"license_number": f"DEL-{uuid.uuid4().hex[:8]}", "full_name": "Owned By Deletable User"},
        headers=owner_headers,
    ).json()

    deleted = client.delete(f"/users/{user_id}", headers=admin_auth_headers)
    assert deleted.status_code == 204

    still_there = client.get(f"/drivers/{driver['id']}", headers=admin_auth_headers)
    assert still_there.status_code == 200


def test_delete_user_with_audit_history_conflicts(client, admin_auth_headers):
    """Unlike drivers, AuditLog.user_id has no ORM relationship() on User, so
    it's never auto-nulled -- a user who has ever acted as an admin (and thus
    has audit_log rows attributed to them) can't be deleted, by design."""
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "ADMIN"},
        headers=admin_auth_headers,
    ).json()["id"]

    tok = client.post("/auth/token", data={"username": email, "password": "supersecret1"})
    new_admin_headers = {"Authorization": f"Bearer {tok.json()['access_token']}"}
    client.post(
        "/users",
        json={"email": _email(), "password": "supersecret1", "role": "FLEET_MANAGER"},
        headers=new_admin_headers,
    )

    conflict = client.delete(f"/users/{user_id}", headers=admin_auth_headers)
    assert conflict.status_code == 409


def test_audit_log_records_admin_actions(client, admin_auth_headers):
    email = _email()
    user_id = client.post(
        "/users",
        json={"email": email, "password": "supersecret1", "role": "FLEET_MANAGER"},
        headers=admin_auth_headers,
    ).json()["id"]
    client.patch(f"/users/{user_id}/role", json={"role": "INSURER"}, headers=admin_auth_headers)
    client.delete(f"/users/{user_id}", headers=admin_auth_headers)

    logs = client.get("/audit-logs", params={"limit": 500}, headers=admin_auth_headers).json()
    actions_for_user = [
        (entry["action"], entry["resource_id"]) for entry in logs if entry["resource_id"] == user_id
    ]
    assert ("create", user_id) in actions_for_user
    assert ("role_change", user_id) in actions_for_user
    assert ("delete", user_id) in actions_for_user
