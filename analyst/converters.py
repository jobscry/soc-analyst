import re
from ipaddress import AddressValueError, IPv4Address
from typing import Pattern, Union

from falcon.routing.converters import BaseConverter

DEFAULT_LOWERCASE_ALPHA_NUM_RE = re.compile(r'[a-zA-Z0-9\-_]{3,}')

class LowerCaseAlphaNumConverter(BaseConverter):
    def __init__(self, pattern: Pattern=DEFAULT_LOWERCASE_ALPHA_NUM_RE):
        self.pattern = pattern

    def convert(self, value: str) -> Union[str, None]:
        if self.pattern.match(value) is None:
            return None
        return value.lower()

class IPV4Converter(BaseConverter):
    def convert(self, value:str) -> Union[str, None]:
        try:
            ip = IPv4Address(value)
            return str(ip)
        except AddressValueError:
            return None
