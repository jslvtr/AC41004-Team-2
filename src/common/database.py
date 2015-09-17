import pymongo
import pymongo.errors

__author__ = 'jamiekerr'


class Database(object):
    def __init__(self, user, password, url, port, database):
        client = pymongo.MongoClient(host=url,
                                     port=port)
        self.database = client[database]
        self.database.authenticate(user, password)

    @staticmethod
    def find(collection, query):
        if collection is not None:
            return collection.find(query)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def find_one(collection, query):
        if collection is not None:
            return collection.find_one(query)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def insert(collection, data):
        if collection is not None:
            return collection.insert(data)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def update(collection, query, data):
        if collection is not None:
            return collection.update(query, data)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def remove(collection, query):
        if collection is not None:
            return collection.remove(query)
        else:
            raise pymongo.errors.InvalidOperation
