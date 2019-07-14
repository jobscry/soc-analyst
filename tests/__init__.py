import pytest
from falcon import testing

from analyst.app import AnalystService

TEST_CONFIG = {
    'db': {
        'file_path': ':memory:'
    },
    'asn_path': './etc/analyst/GeoLite2-ASN/GeoLite2-ASN.mmdb',
    'geo_path': './etc/analyst/GeoLite2-City/GeoLite2-City.mmdb'
}


@pytest.fixture()
def client():
    return testing.TestClient(AnalystService(cfg=TEST_CONFIG))
