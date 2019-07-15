import json

import pytest
from falcon import HTTPBadRequest
from tests import client, superuser

from analyst.models.iplist import IPList, IPListItem, ListItem
from analyst.models.user import User, create_user


def test_iplistresource_list_on_get(client, superuser):
    resp = client.simulate_get(
        "/api/test/iplists", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "iplists" in resp.json


def test_iplistresource_on_get_found(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    resp = client.simulate_get(
        "/api/test/iplists/test-list", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert resp.json["iplist"]["name"] == ip_list.name


def test_iplistresource_on_post_ok(client, superuser):
    json = {"name": "test-list"}
    resp = client.simulate_post(
        "/api/test/iplists", headers={"Authorization": f"Token {superuser}"}, json=json
    )
    assert resp.status_code == 201
    assert resp.json["status"] == "Success"


def test_iplistresource_on_post_bad(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"name": "test-list"}
    resp = client.simulate_post(
        "/api/test/iplists", headers={"Authorization": f"Token {superuser}"}, json=json
    )
    assert resp.status_code == 400


def test_iplistresource_on_put_ok(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"description": "test-list"}
    resp = client.simulate_put(
        "/api/test/iplists/test-list",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "Success"


def test_iplistresource_on_delete_ok(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    resp = client.simulate_delete(
        "/api/test/iplists/test-list", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert resp.json["status"] == "Success"


def test_iplistitemresource_on_get_found(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    resp = client.simulate_get(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
    )
    assert resp.status_code == 200


def test_iplistitemresource_on_post_all_new(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1", "9.9.9.9"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 201
    assert ListItem.select().count() == 2
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 2


def test_iplistitemresource_on_post_some_new(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1", "9.9.9.9"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    json = {"ips": ["1.1.1.1", "1.0.0.1"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 201
    assert ListItem.select().count() == 3
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 3


def test_iplistitemresource_on_post_none_new(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1", "9.9.9.9"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert ListItem.select().count() == 2
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 2


def test_iplistitemresource_on_post_notes(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1"], "note": "test note "}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 201
    ip = ListItem.get(ip="1.1.1.1")
    list_item = IPListItem.get(id=1)
    assert list_item.note == "test note"


def test_iplistitemresource_on_delete_remove_none(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 1
    json = {"ips": ["2.2.2.2"]}
    resp = client.simulate_delete(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert resp.json["count_removed"] == 0
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 1


def test_iplistitemresource_on_delete_remove_some(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1", "2.2.2.2"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 2
    json = {"ips": ["2.2.2.2"]}
    resp = client.simulate_delete(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert resp.json["count_removed"] == 1
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 1


def test_iplistitemresource_on_delete_remove_all(client, superuser):
    ip_list = IPList(name="test-list", created_by=User.get_by_token(superuser))
    ip_list.save()
    json = {"ips": ["1.1.1.1", "2.2.2.2"], "note": "test note"}
    resp = client.simulate_post(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 2
    json = {"ips": ["2.2.2.2", "1.1.1.1"]}
    resp = client.simulate_delete(
        "/api/test/iplists/test-list/items",
        headers={"Authorization": f"Token {superuser}"},
        json=json,
    )
    assert resp.status_code == 200
    assert resp.json["count_removed"] == 2
    assert IPListItem.select().where((IPListItem.ip_list == ip_list)).count() == 0
