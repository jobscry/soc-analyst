import json

import pytest
from tests import client, superuser

from analyst.models.user import create_user


def test_user_on_get_notfound(client, superuser):
    resp = client.simulate_get(
        "/api/test/users/not-found", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404


def test_user_on_get_found(client, superuser):
    resp = client.simulate_get(
        "/api/test/users/superuser", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "user" in resp.json


def test_user_on_get_found_not_admin_bad(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users/superuser", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_user_on_get_found_not_admin_ok(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users/test-user", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 200
    assert "user" in resp.json


def test_user_on_gest_list_not_admin(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_user_on_gest_list_is_admin(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "users" in resp.json
