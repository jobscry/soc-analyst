import pytest
from falcon import testing

from analyst.app import AnalystService


class TestDBConfig:
    def __init__(self):
        self.file_path = ":memory:"


class TestConfig:
    def __init__(self):
        self.db = TestDBConfig()
        self.asn_path = "./etc/analyst/GeoLite2-ASN/GeoLite2-ASN.mmdb"
        self.geo_path = "./etc/analyst/GeoLite2-City/GeoLite2-City.mmdb"
        self.version = "1"


@pytest.fixture()
def client():
    return testing.TestClient(AnalystService(cfg=TestConfig()))
