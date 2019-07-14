from tests import client

from analyst.models.user import User


def test_user_str():
    u = User(username="tester")
    assert str(u) == "tester"


def test_user_get_by_token_none(client):
    u = User(username="tester")
    u.token = "test-token"
    u.is_active = False
    u.save()
    assert User.get_by_token("test-token") is None


def test_user_get_by_token_not_none(client):
    u = User(username="tester")
    u.token = "test-token"
    u.is_active = True
    u.save()
    u2 = User.get_by_token("test-token")
    assert u2 is not None
    assert u2.id == u.id


def test_user_get_by_basic_auth_none(client):
    username = "tester"
    password = "test-password"
    u = User(username=username)
    u.token = "test-token"
    u.is_active = False
    u.set_password(password)
    u.save()
    assert User.get_by_basic_auth(username=username, password=password) is None


def test_user_get_by_basic_auth_not_none(client):
    username = "tester"
    password = "test-password"
    u = User(username=username)
    u.token = "test-token"
    u.is_active = True
    u.set_password(password)
    u.save()
    u2 = User.get_by_basic_auth(username=username, password=password)
    assert u2 is not None
    assert u.id == u2.id
