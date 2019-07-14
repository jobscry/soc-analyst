import pytest
from falcon import HTTPNotAcceptable

from analyst.middleware.json import RequireJSONMiddleware


class TestReq:
    def __init__(self, accepts_json: bool = True):
        self.client_accepts_json = accepts_json


def test_requirejsonmiddleware_bad():
    middleware = RequireJSONMiddleware()
    with pytest.raises(HTTPNotAcceptable):
        middleware.process_request(req=TestReq(False), resp=None)


def test_requirejsonmiddleware_good():
    middleware = RequireJSONMiddleware()
    middleware.process_request(req=TestReq(True), resp=None)
