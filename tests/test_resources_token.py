import pytest
from tests import client, superuser
import json

from analyst.models.user import create_user


def test_token_on_put_notfound(client, superuser):
    resp = client.simulate_put(
        "/api/test/tokens/notfound", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404


def test_token_on_put_is_admin(client, superuser):
    resp = client.simulate_put(
        "/api/test/tokens/superuser", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "token" in resp.json


def test_token_on_put_is_not_admin_bad(client, superuser):
    u = create_user("test-user", "test-user")
    resp = client.simulate_put(
        "/api/test/tokens/superuser", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_token_on_put_is_not_admin_ok(client, superuser):
    u = create_user("test-user", "test-user")
    resp = client.simulate_put(
        "/api/test/tokens/test-user", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 200
    assert "token" in resp.json


def test_token_on_get_notfound(client, superuser):
    resp = client.simulate_get(
        "/api/test/tokens/not-found", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404


def test_token_on_get_found_is_admin(client, superuser):
    u = create_user("test-user", "test-user")
    resp = client.simulate_get(
        "/api/test/tokens/test-user", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "token" in resp.json


def test_token_on_get_found_is_not_admin_bad(client, superuser):
    u = create_user("test-user", "test-user")
    resp = client.simulate_get(
        "/api/test/tokens/superuser", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_token_on_get_found_is_not_admin_ok(client, superuser):
    u = create_user("test-user", "test-user")
    resp = client.simulate_get(
        "/api/test/tokens/test-user", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 200
    assert "token" in resp.json
