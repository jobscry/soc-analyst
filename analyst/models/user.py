import secrets
from typing import Union

import peewee
from passlib.hash import pbkdf2_sha256

from analyst.models import BaseModel

API_KEY_BYTES = 64


class User(BaseModel):
    username = peewee.CharField(unique=True, max_length=50)
    token = peewee.CharField(unique=True)
    password = peewee.CharField(null=True)
    is_active = peewee.BooleanField(default=True)
    is_admin = peewee.BooleanField(default=False)
    is_manager = peewee.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username

    def set_password(self, password: str) -> None:
        """
        Set Password

        Params:

        * **password**  String, no requirements.

        Returns nothing.

        If `can_login` is True, sets the password for the current user to `password`.

        Password is salted, hashed with `pbkdf2_sha256` via passlib.

        This does not save the user.
        """

        self.password = pbkdf2_sha256.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify Password

        Params:

        * **password**  String, no requirements.

        Returns: Boolean, does this password match the user's password?

        Password is verified with `pbkf2_sha256` via passlib.
        """

        return pbkdf2_sha256.verify(password, self.password)  # pragma: no cover

    @staticmethod
    def get_by_token(token: str) -> Union[None, BaseModel]:
        """
        Get by Token (static)

        Params:

        * **token** String.

        Returns: Active user with `token` or None.

        Used by authentication middlware.  Will not return a user if the `is_active` is False.
        """
        return User.get_or_none(User.token == token, User.is_active)

    @staticmethod
    def get_by_basic_auth(username: str, password: str) -> Union[None, BaseModel]:
        """
        Get by Basic Auth

        Params:

        * **username**  String
        * **password**  String

        Returns: Active user with `username` and `password` or None.

        Used by authentication middleware.  Will not return a user if `is_active` is False.
        """
        try:
            user = User.get(username=username.strip().lower(), is_active=True)
            if user.verify_password(password):
                return user
        except peewee.DoesNotExist:
            pass
        return None

    def generate_token(self) -> None:
        """
        Generate Token

        Returns: String, new token.
        """
        self.token = secrets.token_urlsafe(API_KEY_BYTES)


def create_user(
    username: str,
    password: str,
    is_admin: bool = False,
    is_manager: bool = False,
    is_active: bool = True,
) -> str:
    """
    Create User

    Params:

    * **username**  String, required.
    * **password**  String, required, will be set through `set_password`.

    Returns: String, new user's new token.
    """
    u = User(
        username=username.strip().lower(),
        is_admin=is_admin,
        is_manager=is_manager,
        is_active=is_active,
    )

    u.set_password(password)
    u.generate_token()
    u.save()

    return u.token
