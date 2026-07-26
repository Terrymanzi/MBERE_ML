"""GET /drivers search — case-insensitive over full_name / license_number."""
from __future__ import annotations

import uuid


def _license() -> str:
    return f"RW-{uuid.uuid4().hex[:8].upper()}"


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
