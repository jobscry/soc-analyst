import falcon
import geoip2.database
from falcon.media.validators.jsonschema import validate

from analyst.resources import BaseResource
from analyst.schemas import load_schema


class GeoResource(BaseResource):
    def __init__(self, geo_path):
        self.geo_path = geo_path

    @validate(load_schema("asn"))
    def on_post(self, req: falcon.Request, resp: falcon.Response, ip: str = None):
        results = list()
        with geoip2.database.Reader(self.geo_path) as reader:
            for ip in req.media.get("ips", None):
                try:
                    lookup = reader.city(ip)
                    results.append(
                        {
                            "city": lookup.city.name,
                            "continent": lookup.continent.name,
                            "lat": lookup.location.latitude,
                            "lon": lookup.location.longitude,
                            "country": lookup.country.name,
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

        with geoip2.database.Reader(self.geo_path) as reader:
            try:
                lookup = reader.city(ip)
                resp.media = {
                    "city": lookup.city.name,
                    "continent": lookup.continent.name,
                    "lat": lookup.location.latitude,
                    "lon": lookup.location.longitude,
                    "country": lookup.country.name,
                }
            except geoip2.errors.AddressNotFoundError:
                raise falcon.HTTPBadRequest("Bad Request", "No response for query.")
            except ValueError:
                raise falcon.HTTPBadRequest("Bad Request", "Not a valid IPv4 address.")
