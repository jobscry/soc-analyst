import falcon
from falcon_auth import (BasicAuthBackend, FalconAuthMiddleware,
                         MultiAuthBackend, TokenAuthBackend)

from analyst.converters import IPV4Converter, LowerCaseAlphaNumConverter
from analyst.middleware.cors import CORSComponentMiddleware
from analyst.middleware.json import RequireJSONMiddleware
from analyst.models.manager import DBManager
from analyst.models.user import User
from analyst.resources import asn, geo, iplists, tokens, users
from analyst.serializers.datetime import DateTimeJSONHandler


class AnalystService(falcon.API):
    def __init__(self, cfg):
        token_auth = TokenAuthBackend(User.get_by_token)
        basic_auth = BasicAuthBackend(User.get_by_basic_auth)
        multi_auth = MultiAuthBackend(token_auth, basic_auth)
        auth_middleware = FalconAuthMiddleware(multi_auth)

        super(AnalystService, self).__init__(
            middleware=[
                CORSComponentMiddleware(),
                RequireJSONMiddleware(),
                auth_middleware,
            ],
            media_type="application/json",
        )

        handlers = falcon.media.Handlers({"application/json": DateTimeJSONHandler()})
        self.resp_options.media_handlers.update(handlers)
        self.resp_options.default_media_type = "application/json",
        self.router_options.converters['ipv4_addr'] = IPV4Converter
        self.router_options.converters['lowercase_alpha_num'] = LowerCaseAlphaNumConverter

        self.cfg = cfg

        # Build an object to manage our db connections.
        self.manager = DBManager(self.cfg.db.file_path)
        self.manager.setup()

        # Build routes
        self.add_route(f"/api/{self.cfg.version}/init", users.InitResource())
        self.add_route(f"/api/{self.cfg.version}/user", users.UsersResource())
        self.add_route(
            f"/api/{self.cfg.version}/users/{{username:lowercase_alpha_num}}", users.UsersResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/tokens/{{username:lowercase_alpha_num}}", tokens.TokensResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/asn", asn.ASNResource(self.cfg.asn_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/asn/{{ip:ipv4_addr}}", asn.ASNResource(self.cfg.asn_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/geo", geo.GeoResource(self.cfg.geo_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/geo/{{ip:ipv4_addr}}", geo.GeoResource(self.cfg.geo_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists", iplists.IPListResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists/{{ip_list_name:lowercase_alpha_num}}", iplists.IPListResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists/{{ip_list_name:lowercase_alpha_num}}/items", iplists.IPListItemResource()
        )

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        self.manager.close()
