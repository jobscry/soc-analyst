import falcon
from falcon_auth import (
    BasicAuthBackend,
    FalconAuthMiddleware,
    MultiAuthBackend,
    TokenAuthBackend,
)

from analyst.models.manager import DBManager
from analyst.middleware.cors import CORSComponentMiddleware
from analyst.middleware.json import RequireJSONMiddleware
from analyst.models.user import User
from analyst.resources import asn, geo, tokens, users, iplists
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
        self.resp_options.default_media_type = "application/json"

        self.cfg = cfg

        # Build an object to manage our db connections.
        self.manager = DBManager(self.cfg.db.file_path)
        self.manager.setup()

        # Build routes
        self.add_route(f"/api/{self.cfg.version}/init", users.InitResource())
        self.add_route(f"/api/{self.cfg.version}/user", users.UsersResource())
        self.add_route(
            f"/api/{self.cfg.version}/users/{{username}}", users.UsersResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/tokens/{{username}}", tokens.TokensResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/asn", asn.ASNResource(self.cfg.asn_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/asn/{{ip}}", asn.ASNResource(self.cfg.asn_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/geo", geo.GeoResource(self.cfg.geo_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/geo/{{ip}}", geo.GeoResource(self.cfg.geo_path)
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists", iplists.IPListResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists/{{ip_list_name}}", iplists.IPListResource()
        )
        self.add_route(
            f"/api/{self.cfg.version}/iplists/{{ip_list_name}}/items", iplists.IPListItemResource()
        )

    def start(self):
        """ A hook to when a Gunicorn worker calls run()."""
        pass

    def stop(self, signal):
        """ A hook to when a Gunicorn worker starts shutting down. """
        self.manager.close()
