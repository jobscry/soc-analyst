import falcon
import geoip2.database
from falcon.media.validators.jsonschema import validate

from analyst.resources import BaseResource
from analyst.schemas import load_schema


class ASNResource(BaseResource):
    def __init__(self, asn_path):
        self.asn_path = asn_path

    @validate(load_schema("asn"))
    def on_post(self, req: falcon.Request, resp: falcon.Response, ip: str = None):
        results = list()
        with geoip2.database.Reader(self.asn_path) as reader:
            for ip in req.media.get('ips', None):
                try:
                    lookup = reader.asn(ip)
                    results.append(
                        {
                            "ip": lookup.ip_address,
                            "asn_number": lookup.autonomous_system_number,
                            "asn_org": lookup.autonomous_system_organization,
                        }
                    )
                except geoip2.errors.AddressNotFoundError:
                    raise falcon.HTTPBadRequest("Bad Request", "No response for query.")
                except ValueError:
                    raise falcon.HTTPBadRequest(
                        "Bad Request", "Not a valid IPv4 address."
                    )

        resp.media = results

    def on_get(self, req: falcon.Request, resp: falcon.Response, ip: str = None):
        if ip is None:
            raise falcon.HTTPNotFound()

        with geoip2.database.Reader(self.asn_path) as reader:
            try:
                lookup = reader.asn(ip)
                resp.media = {
                    "ip": lookup.ip_address,
                    "asn_number": lookup.autonomous_system_number,
                    "asn_org": lookup.autonomous_system_organization,
                }
            except geoip2.errors.AddressNotFoundError:
                raise falcon.HTTPBadRequest("Bad Request", "No response for query.")
            except ValueError:
                raise falcon.HTTPBadRequest("Bad Request", "Not a valid IPv4 address.")
