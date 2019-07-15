from functools import wraps
from typing import Callable

import falcon


class BaseResource:
    def __init__(self):
        pass


def check_permission(check_func: Callable) -> Callable:
    def decorator(func):
        def wrapper(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
            if not check_func(req.context["user"]):
                raise falcon.HTTPUnauthorized(
                    "Unauthorized", "Insufficient privileges for method"
                )
            return func(self, req, resp, *args, **kwargs)

        return wrapper

    return decorator
