import datetime
from src.common.database import Database
from src.models.user import User

__author__ = 'jslvtr'


class PointType(object):
    COLLECTION = "point_types"

    def __init__(self, name, date=datetime.datetime.utcnow()):
        self.name = name
        self.date = date

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
            "name": self.name,
            "date": self.date
        }

        return json

    def users_with_point(self):
        users = Database.find(User.COLLECTION, {"points.{}".format(self.name): {"$exists": True}})
        total = 0
        for user in users:
            total += user['points'][self.name]

        return total

    @staticmethod
    def get_point_types():
        return [point_type['name'] for point_type in Database.find(collection=PointType.COLLECTION,
                                                       query={})]