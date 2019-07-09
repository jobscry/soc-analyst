import ipaddress
import peewee

from analyst.models import BaseModel
from analyst.models.user import User


class ListItem(BaseModel):
    ip = peewee.IPField(unique=True)


class IPList(BaseModel):
    name = peewee.CharField(max_length=255, unique=True)
    description = peewee.TextField(null=True)
    is_active = peewee.BooleanField(default=True)
    created_by = peewee.ForeignKeyField(User)


class IPListItem(BaseModel):
    ip = peewee.ForeignKeyField(ListItem)
    blacklist = peewee.ForeignKeyField(IPList)
    added_by = peewee.ForeignKeyField(User)
    note = peewee.CharField(null=True)
