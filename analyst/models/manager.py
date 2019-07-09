from peewee import *
from analyst.models.user import User
from analyst.models.iplist import ListItem, IPList, IPListItem


class DBManager:
    def __init__(self, db_path: str, db_classes: list = [User, ListItem, IPList, IPListItem]):
        self.db_path = db_path
        self.db_classes = db_classes
        self.db = None

    def setup(self):
        self.db = SqliteDatabase(self.db_path)
        self.db.bind(self.db_classes)
        self.db.create_tables(self.db_classes)
