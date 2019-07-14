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


def test_user_on_get_list_not_admin(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_user_on_get_list_is_admin(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_get(
        "/api/test/users", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "users" in resp.json


def test_user_on_post_not_admin(client):
    u = create_user("test-user", "test-password")
    json = {"username": "another-test-user", "password": "another-test-password"}
    resp = client.simulate_post(
        "/api/test/users", headers={"Authorization": f"Token {u}"}, json=json
    )
    assert resp.status_code == 403


def test_user_on_post_is_admin(client, superuser):
    json = {"username": "another-test-user", "password": "another-test-password"}
    resp = client.simulate_post(
        "/api/test/users", headers={"Authorization": f"Token {superuser}"}, json=json
    )
    assert resp.status_code == 201
    assert resp.json["status"] == "Success"


def test_user_on_post_is_admin_username_exists(client, superuser):
    u = create_user("test-user", "test-password")
    json = {"username": "test-user", "password": "test-password"}
    resp = client.simulate_post(
        "/api/test/users", headers={"Authorization": f"Token {superuser}"}, json=json
    )
    assert resp.status_code == 400


def test_user_on_put_not_admin_bad(client):
    create_user("test-user", "test-password")
    u = create_user("-another-test-user", "another-test-password")
    json = {"password": "another-test-password"}
    resp = client.simulate_put(
        "/api/test/users/test-user", headers={"Authorization": f"Token {u}"}, json=json
    )
    assert resp.status_code == 403


def test_user_on_put_not_admin_ok(client, superuser):
    u = create_user("test-user", "test-password")
    json = {"password": "another-test-password"}
    resp = client.simulate_put(
        "/api/test/users/superuser", headers={"Authorization": f"Token {u}"}, json=json
    )
    assert resp.status_code == 403


def test_user_on_put_not_admin_bad_own_attributes(client):
    u = create_user("test-user", "test-password")
    json = {"is_admin": True}
    resp = client.simulate_put(
        "/api/test/users/test-user", headers={"Authorization": f"Token {u}"}, json=json
    )
    assert resp.status_code == 403


def test_user_on_put_is_admin(client, superuser):
    create_user("test-user", "test-password")
    json = {
        "password": "another-test-password",
        "is_admin": True,
        "is_manager": True,
        "is_active": False,
    }
    resp = client.simulate_put(
        "/api/test/users/test-user",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "Success"


def test_user_on_put_is_admin_not_fond(client, superuser):
    json = {
        "password": "another-test-password",
        "is_admin": True,
        "is_manager": True,
        "is_active": False,
    }
    resp = client.simulate_put(
        "/api/test/users/test-user",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 404


def test_user_on_delete_is_not_admin(client, superuser):
    u = create_user("test-user", "test-password")
    resp = client.simulate_delete(
        "/api/test/users/superuser", headers={"Authorization": f"Token {u}"}
    )
    assert resp.status_code == 403


def test_user_on_delete_is_admin_not_found(client, superuser):
    resp = client.simulate_delete(
        "/api/test/users/test-user", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404
    resp = client.simulate_delete(
        "/api/test/users", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404


def test_user_on_delete_is_admin_delete_self(client, superuser):
    resp = client.simulate_delete(
        "/api/test/users/superuser", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 400


def test_user_on_delete_is_admin_delete_ok(client, superuser):
    create_user("test-user", "test-password")
    resp = client.simulate_delete(
        "/api/test/users/test-user", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "Success"


def test_initresource_on_post_bad(client, superuser):
    json = {"username": "test-admin", "password": "test-admin-password"}
    resp = client.simulate_post("/api/test/init", json=json)
    assert resp.status_code == 400


def test_initresource_on_post_ok(client):
    json = {"username": "test-admin", "password": "test-admin-password"}
    resp = client.simulate_post("/api/test/init", json=json)
    assert resp.status_code == 201
    assert resp.json["status"] == "Success"
