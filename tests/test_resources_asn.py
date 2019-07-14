import pytest
from tests import client, superuser
import json


def test_asn_post_ok(client, superuser):
    resp = client.simulate_post(
        "/api/test/asn",
        headers={"Authorization": f"Token {superuser}"},
        json={"ips": ["1.1.1.1"]},
    )
    assert resp.status_code == 200
    assert len(resp.json) == 1


def test_asn_get_notfound(client, superuser):
    resp = client.simulate_get(
        "/api/test/asn", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 404


def test_asn_get_found(client, superuser):
    resp = client.simulate_get(
        "/api/test/asn/1.1.1.1", headers={"Authorization": f"Token {superuser}"}
    )
    assert resp.status_code == 200
    assert "ip" in resp.json
