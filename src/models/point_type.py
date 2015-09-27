from src.common.database import Database

__author__ = 'jslvtr'


class PointType(object):
    COLLECTION = "point_types"

    def __init__(self, name):
        self.name = name

    @classmethod
    def find_by_name(cls, name):
        data = Database.find_one(collection=cls.COLLECTION,
                                 query={'name': name})
        del data['_id']
        return cls(**data)

    def save_to_db(self):
        Database.update(self.COLLECTION, {"name": self.name}, {'$set': self.json()}, upsert=True)

    def remove_from_db(self):
        Database.remove(self.COLLECTION, {'name': self.name})

    def json(self):
        json = {
            "name": self.name
        }

        return json

    @staticmethod
    def get_point_types():
        return [point_type['name'] for point_type in Database.find(collection=PointType.COLLECTION,
                                                       query={})]