from src.common.database import Database

__author__ = 'jslvtr'


class Permissions(object):
    COLLECTION = "permissions"

    TYPE_ADMIN = "admin"
    TYPE_EVENT = "events"
    TYPE_ARTICLE = "articles"
    TYPE_USER = "user"

    TYPES = [TYPE_ADMIN, TYPE_EVENT, TYPE_ARTICLE, TYPE_USER]

    def __init__(self, name, access, default=0):
        self.name = name
        Permissions._check_access_list(access)
        self.access = access
        self.default = default

    @staticmethod
    def _check_access_list(access):
        if not isinstance(access, list):
            raise PermissionsCreationError("The access parameter must be a list")
        for level in access:
            if level not in Permissions.TYPES:
                raise PermissionsCreationError(
                    "The access parameter had an access type that is not allowed (only use {})".format(
                        Permissions.TYPES))

    @classmethod
    def default(cls):
        data = Database.find_one(collection=cls.COLLECTION,
                                 query={'default': 1})
        del data['_id']
        return cls(**data)

    @classmethod
    def find_by_name(cls, name):
        data = Database.find_one(collection=cls.COLLECTION,
                                 query={'name': name})
        del data['_id']
        return cls(**data)

    @classmethod
    def access_to(cls, type):
        """
        Returns what access levels are allowed to visit a specific type of page or artifact

        When accessing the admin page, call user.permissions.allowed(Permissions.access_to('admin'))
        :param type:
        :return:
        """

        if type not in Permissions.TYPES:
            raise PermissionsCreationError(
                "The type parameter had an access type that is not allowed (only use {})".format(Permissions.TYPES))
        access_levels = Database.find(cls.COLLECTION, {"access": {'$in': [type]}})
        return [level['name'] for level in access_levels]

    @classmethod
    def set_default(cls, name):
        try:
            current_default = cls.default()
            new_default = cls.find_by_name(name)

            current_default.default = 0
            current_default.save_to_db()

            new_default.default = 1
            new_default.save_to_db()
            return True
        except:
            return False

    def allowed(self, access_levels):
        return self.name in [level for level in access_levels]

    def save_to_db(self):
        Database.update(self.COLLECTION, {"name": self.name}, {'$set': self.json()}, upsert=True)

    def json(self):
        json = {
            "name": self.name,
            "access": self.access,
            "default": self.default
        }

        return json


class PermissionsCreationError(Exception):
    pass
