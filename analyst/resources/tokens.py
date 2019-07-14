import falcon
from peewee import DoesNotExist

from analyst.models.user import User
from analyst.resources import BaseResource


class TokensResource(BaseResource):
    def on_post(self, req: falcon.Request, resp: falcon.Response, username: str):
        try:
            user = User.get(username=username)

            if not req.context["user"].is_admin and req.context["user"].id != user.id:
                raise falcon.HTTPForbidden(
                    "Forbidden", "Insufficient privileges for operation."
                )

            user.generate_token()
            user.save()

            resp.media = {"token": user.token}

        except DoesNotExist:
            raise falcon.HTTPNotFound()

    def on_get(self, req: falcon.Request, resp: falcon.Response, username: str):
        try:
            user = User.get(username=username)

            if not req.context["user"].is_admin and req.context["user"].id != user.id:
                raise falcon.HTTPForbidden(
                    "Forbidden", "Insufficient privileges for operation."
                )

            resp.media = {"token": user.token}

        except DoesNotExist:
            raise falcon.HTTPNotFound()
