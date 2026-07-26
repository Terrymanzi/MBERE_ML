"""GET /drivers search, plus per-owner data isolation."""
from __future__ import annotations

import uuid


def _license() -> str:
    return f"RW-{uuid.uuid4().hex[:8].upper()}"


def _register_and_login(client) -> dict[str, str]:
    email = f"owner-{uuid.uuid4().hex[:8]}@test.com"
    password = "supersecret1"
    reg = client.post("/auth/register", json={"email": email, "password": password})
    assert reg.status_code == 201, reg.text
    tok = client.post("/auth/token", data={"username": email, "password": password})
    assert tok.status_code == 200, tok.text
    return {"Authorization": f"Bearer {tok.json()['access_token']}"}


def test_search_matches_name_or_license_case_insensitively(client, auth_headers):
    a = client.post(
        "/drivers",
        json={"license_number": _license(), "full_name": "Aline Uwase"},
        headers=auth_headers,
    ).json()
    b = client.post(
        "/drivers",
        json={"license_number": _license(), "full_name": "Jean-Paul Niyonzima"},
        headers=auth_headers,
    ).json()

    by_name = client.get("/drivers", params={"q": "aline"}, headers=auth_headers)
    assert by_name.status_code == 200
    ids = {d["id"] for d in by_name.json()}
    assert a["id"] in ids
    assert b["id"] not in ids

    by_license = client.get(
        "/drivers", params={"q": b["license_number"][:5]}, headers=auth_headers
    )
    assert {d["id"] for d in by_license.json()} == {b["id"]}


def test_search_with_no_matches_returns_empty_list(client, auth_headers):
    r = client.get("/drivers", params={"q": "no-such-driver-xyz"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_blank_search_behaves_like_no_search(client, auth_headers):
    license_number = _license()
    client.post(
        "/drivers",
        json={"license_number": license_number, "full_name": "Blank Query Tester"},
        headers=auth_headers,
    )
    r = client.get("/drivers", params={"q": "   "}, headers=auth_headers)
    assert r.status_code == 200
    assert any(d["license_number"] == license_number for d in r.json())


def test_list_drivers_scoped_to_owner(client):
    owner_a = _register_and_login(client)
    owner_b = _register_and_login(client)

    driver_a = client.post(
        "/drivers", json={"license_number": _license(), "full_name": "Owner A's Driver"}, headers=owner_a
    ).json()
    driver_b = client.post(
        "/drivers", json={"license_number": _license(), "full_name": "Owner B's Driver"}, headers=owner_b
    ).json()

    a_ids = {d["id"] for d in client.get("/drivers", headers=owner_a).json()}
    b_ids = {d["id"] for d in client.get("/drivers", headers=owner_b).json()}

    assert driver_a["id"] in a_ids and driver_b["id"] not in a_ids
    assert driver_b["id"] in b_ids and driver_a["id"] not in b_ids


def test_get_update_delete_and_risk_history_404_for_non_owner(client):
    owner = _register_and_login(client)
    other = _register_and_login(client)

    driver = client.post(
        "/drivers", json={"license_number": _license(), "full_name": "Private Driver"}, headers=owner
    ).json()
    driver_id = driver["id"]

    assert client.get(f"/drivers/{driver_id}", headers=other).status_code == 404
    assert (
        client.put(f"/drivers/{driver_id}", json={"full_name": "Hijacked"}, headers=other).status_code
        == 404
    )
    assert client.get(f"/risk/{driver_id}", headers=other).status_code == 404
    assert client.delete(f"/drivers/{driver_id}", headers=other).status_code == 404

    # owner themself is unaffected
    assert client.get(f"/drivers/{driver_id}", headers=owner).status_code == 200


def test_admin_sees_and_can_access_any_driver(client, admin_auth_headers):
    owner = _register_and_login(client)
    driver = client.post(
        "/drivers", json={"license_number": _license(), "full_name": "Admin Visible Driver"}, headers=owner
    ).json()
    driver_id = driver["id"]

    listed_ids = {d["id"] for d in client.get("/drivers", headers=admin_auth_headers).json()}
    assert driver_id in listed_ids
    assert client.get(f"/drivers/{driver_id}", headers=admin_auth_headers).status_code == 200
    assert client.get(f"/risk/{driver_id}", headers=admin_auth_headers).status_code == 200
