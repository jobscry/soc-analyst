from datetime import datetime
from functools import singledispatch

from falcon.media.json import JSONHandler
from falcon.util import json

# https://hynek.me/articles/serialization/


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat() + "Z"


class DateTimeJSONHandler(JSONHandler):
    def serialize(self, media, content_type):
        result = json.dumps(media, ensure_ascii=False, default=to_serializable)
        return result.encode("utf-8")
