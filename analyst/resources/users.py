import falcon
from falcon.media.validators.jsonschema import validate
from peewee import DoesNotExist, IntegrityError

from analyst.models.user import User, create_user
from analyst.resources import BaseResource, check_permission
from analyst.schemas import load_schema


class UsersResource(BaseResource):
    def on_get(self, req: falcon.Request, resp: falcon.Response, username: str = None):
        if username is None:
            if not req.context["user"].is_admin:
                raise falcon.HTTPForbidden(
                    "Forbidden", "Insufficient privileges for operation."
                )

            user = User.select(
                User.username,
                User.is_active,
                User.is_admin,
                User.is_manager,
                User.created_on,
            )

            resp.media = {"users": list(user.dicts())}

        else:
            user = User.get(User.username == username)
            if not req.context["user"].is_admin and req.context["user"].id != user.id:
                raise falcon.HTTPForbidden(
                    "Forbidden", "Insufficient privileges for operation."
                )

            resp.media = {
                "user": user.to_dict(
                    ["username", "is_active", "is_admin", "is_manager", "created_on"]
                )
            }

    @check_permission(lambda user: user.is_admin)
    @validate(load_schema("create_user"))
    def on_post(self, req: falcon.Request, resp: falcon.Response, username: str = None):
        username = req.media.get("username", None)
        password = req.media.get("password", None)
        is_admin = req.media.get("is_admin", False)
        is_manager = req.media.get("is_manager", False)
        is_active = req.media.get("is_active", True)

        try:
            create_user(username, password, is_admin, is_manager, is_active)
            resp.status = falcon.HTTP_201
            resp.media = {"status": "Success", "message": "New user created."}
        except IntegrityError:
            raise falcon.HTTPBadRequest("Bad Request", "Username already exists.")

    @validate(load_schema("update_user"))
    def on_put(self, req: falcon.Request, resp: falcon.Response, username: str = None):
        user = User.get(User.username == username)
        if not req.context["user"].is_admin and req.context["user"].id != user.id:
            raise falcon.HTTPForbidden(
                "Forbidden", "Insufficient privileges for operation."
            )

        is_admin = req.media.get("is_admin", None)
        is_manager = req.media.get("is_manager", None)
        is_active = req.media.get("is_active", None)

        if req.context["user"].id == user.id and (
            is_admin is not None or is_manager is not None or is_active is not None
        ):
            raise falcon.HTTPForbidden("Forbidden", "Can not modifiy own attributes.")

        password = req.media.get("password", None)
        if password is not None:
            user.set_password(password)
        if is_admin is not None:
            user.is_admin = is_admin
        if is_manager is not None:
            user.is_manager = is_manager
        if is_active is not None:
            user.is_active = is_active

        user.save()
        resp.media = {"status": "Success", "message": "User updated."}

    @check_permission(lambda user: user.is_admin)
    def on_delete(
        self, req: falcon.Request, resp: falcon.Response, username: str = None
    ):
        user = User.get(User.username == username)

        if req.context["user"].id == user.id:
            raise falcon.HTTPBadRequest("Bad Request", "Can not delete self.")

        user.delete_instance()
        resp.media = {"status": "Success", "message": "User deleted."}


class InitResource(BaseResource):
    """
    Initialize Resource

    Creates a single admin user.  Only cllable if no admin user exits.
    """

    auth = {"auth_disabled": True}

    @validate(load_schema("create_user_init"))
    def on_post(self, req: falcon.Request, resp: falcon.Response):

        if User.select().where(User.is_admin).count() > 0:
            raise falcon.HTTPBadRequest("Bad Request", "App already initialized.")

        token = create_user(
            username=req.media.get("username"),
            password=req.media.get("password"),
            is_admin=True,
        )

        resp.status = falcon.HTTP_201
        resp.media = {
            "status": "Success",
            "token": token,
            "message": "First admin user created.",
        }
