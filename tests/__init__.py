import pytest
from falcon import testing

from analyst.app import AnalystService
from analyst.models.user import create_user


class TestDBConfig:
    def __init__(self):
        self.file_path = ":memory:"


class TestConfig:
    def __init__(self):
        self.db = TestDBConfig()
        self.asn_path = "./etc/analyst/GeoLite2-ASN/GeoLite2-ASN.mmdb"
        self.geo_path = "./etc/analyst/GeoLite2-City/GeoLite2-City.mmdb"
        self.version = "test"


@pytest.fixture()
def client():
    return testing.TestClient(AnalystService(cfg=TestConfig()))


@pytest.fixture()
def superuser(client):
    u = create_user(username="superuser", password="password", is_admin=True)
    return u
