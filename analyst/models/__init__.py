from datetime import datetime
from typing import Dict, List, Union

import peewee
from falcon import HTTPNotFound


class BaseModel(peewee.Model):
    created_on = peewee.DateTimeField(default=datetime.utcnow())
    modified_on = peewee.DateTimeField(null=True)

    def save(self, *args, **kwargs) -> int:
        self.modified_on = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self, fields: List[str]) -> Dict[str, str]:
        ret_dict = dict()
        for k in self.__class__()._meta.sorted_field_names:
            if k in fields:
                ret_dict[k] = getattr(self, k)
        return ret_dict

    @classmethod
    def get_or_404(cls, *expressions):
        try:
            return cls.get(*expressions)
        except:
            raise HTTPNotFound
