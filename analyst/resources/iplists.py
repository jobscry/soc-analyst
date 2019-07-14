import falcon

from falcon.media.validators.jsonschema import validate
from peewee import DoesNotExist, IntegrityError

from analyst.models.user import User
from analyst.models.iplist import IPList, ListItem, IPListItem
from analyst.resources import BaseResource
from analyst.schemas import load_schema


class IPListItemResource:
    def on_get(self, req: falcon.Request, resp: falcon.Response, ip_list_name: str):
        try:
            ip_list = IPList.get(name=ip_list_name)
            resp.media = {
                "iplist": ip_list.to_dict(
                    fields=[
                        "name",
                        "description",
                        "created_by",
                        "is_active",
                        "created_on",
                    ]
                )
            }
        except DoesNotExist:
            raise falcon.HTTPNotFound()

    @validate(load_schema("manage_ip_list_items"))
    def on_post(self, req: falcon.Request, resp: falcon.Response, ip_list_name: str):
        if not (req.context["user"].is_admin or req.context["user"].is_manager):
            raise falcon.HTTPBadRequest(
                "Bad Request", "Insufficient priviledges for function."
            )
        try:
            ip_list = IPList.get(name=ip_list_name)

            ips = req.media.get("ips")
            existing_ips = ListItem.select().where(ListItem.ip.in_(ips))

            existing_ips_list = [x.ip for x in list(existing_ips)]
            new_ips_list = list(set(ips) - set(existing_ips_list))

            ListItem.insert_many(
                [(x,) for x in new_ips_list], fields=[ListItem.ip]
            ).execute()

            list_ips = (
                ListItem.select()
                .join(IPListItem)
                .join(IPList)
                .where((IPList.id == ip_list.id), (ListItem.ip.in_(existing_ips_list)))
            )
            list_ips_list = [x.ip for x in list(list_ips)]
            new_list_ips_list = list(set(ips) - set(list_ips_list))

            note = req.media.get("note", None)
            if note:
                note = note.strip()
            ip_list_items = []
            for list_item in ListItem.select().where(
                ListItem.ip.in_(new_list_ips_list)
            ):
                ip_list_items.append((ip_list, list_item, req.context["user"], note))

            IPListItem.insert_many(
                ip_list_items,
                fields=[
                    IPListItem.ip_list,
                    IPListItem.ip,
                    IPListItem.added_by,
                    IPListItem.note,
                ],
            ).execute()

            if len(new_ips_list) > 0 or len(new_list_ips_list) > 0:
                resp.status = falcon.HTTP_201

            resp.media = {
                "requested_ips": ips,
                "created_ips": new_ips_list,
                "ips_added_to_list": new_list_ips_list,
            }

        except DoesNotExist:
            raise falcon.HTTPNotFound()

    @validate(load_schema("delete_ip_list_items"))
    def on_delete(self, req: falcon.Request, resp: falcon.Response, ip_list_name: str):
        if not (req.context["user"].is_admin or req.context["user"].is_manager):
            raise falcon.HTTPBadRequest(
                "Bad Request", "Insufficient priviledges for function."
            )
        try:
            ip_list = IPList.get(name=ip_list_name)

            ips = req.media.get("ips", None)

            remove_ips = ListItem.select().where(ListItem.ip.in_(ips))

            deleted = (
                IPListItem.delete()
                .where((IPListItem.ip_list == ip_list), (IPListItem.ip.in_(remove_ips)))
                .execute()
            )

            resp.media = {"count_removed": deleted, "requested_ips": ips}

        except DoesNotExist:
            raise falcon.HTTPNotFound


class IPListResource:
    def on_get(
        self, req: falcon.Request, resp: falcon.Response, ip_list_name: str = None
    ):
        if ip_list_name is None:
            iplist = IPList.select(
                IPList.name,
                IPList.description,
                IPList.created_by,
                IPList.is_active,
                IPList.is_public,
                IPList.created_on,
            ).dicts()

            resp.media = {"iplists": list(iplist)}
        else:
            try:
                iplist = IPList.get(name=ip_list_name)
                resp.media = {
                    "iplist": iplist.to_dict(
                        fields=[
                            "name",
                            "description",
                            "created_by",
                            "is_active",
                            "is_public",
                            "created_on",
                        ]
                    )
                }
            except DoesNotExist:
                raise falcon.HTTPNotFound()

    @validate(load_schema("create_ip_list"))
    def on_post(
        self, req: falcon.Request, resp: falcon.Response, ip_list_name: str = None
    ):
        if not (req.context["user"].is_admin or req.context["user"].is_manager):
            raise falcon.HTTPBadRequest(
                "Bad Request", "Insufficient priviledges for function."
            )
        try:
            iplist = IPList(
                name=req.media.get("name"),
                description=req.media.get("description", None),
                is_active=req.media.get("is_active", True),
                is_public=req.media.get("is_public", True),
                created_by=req.context["user"],
            )
            iplist.save()
            resp.status = falcon.HTTP_201
            resp.media = {
                "status": "Success",
                "message": "Successfully, created iplist.",
            }
        except IntegrityError:
            raise falcon.HTTPBadRequest("Bad Request", "List with name already exists.")

    @validate(load_schema("update_ip_list"))
    def on_put(
        self, req: falcon.Request, resp: falcon.Response, ip_list_name: str = None
    ):
        if not (req.context["user"].is_admin or req.context["user"].is_manager):
            raise falcon.HTTPBadRequest(
                "Bad Request", "Insufficient priviledges for function."
            )
        try:
            ip_list = IPList.get(name=ip_list_name)

            for k in ("description", "is_active", "is_public"):
                if k in req.media:
                    setattr(ip_list, k, req.media.get(k))
            ip_list.save()

            resp.media = {"status": "Success", "Message": "Updated IP List"}

        except DoesNotExist:
            raise falcon.HTTPNotFound()
