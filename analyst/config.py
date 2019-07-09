from aumbry import Attr, YamlConfig


class DatabaseConfig(YamlConfig):
    __mapping__ = {"file_path": Attr("file_path", str)}

    connection = ""


class AppConfig(YamlConfig):
    __mapping__ = {
        "db": Attr("db", DatabaseConfig),
        "gunicorn": Attr("gunicorn", dict),
        "version": Attr("version", str),
        "asn_path": Attr("asn_path", str),
        "geo_path": Attr("geo_path", str)
    }

    def __init__(self):
        self.db = DatabaseConfig()
        self.gunicorn = {}
        self.version = None
        self.asn_path = None
        self.geo_path = None
