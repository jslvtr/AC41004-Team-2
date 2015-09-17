import pymongo
import pymongo.errors

__author__ = 'jamiekerr'


class Database(object):

    DATABASE = None

    @staticmethod
    def initialize(user, password, url, port, database):
        client = pymongo.MongoClient(host=url,
                                     port=port)
        Database.DATABASE = client[database]
        Database.DATABASE.authenticate(user, password)

    @staticmethod
    def find(collection, query):
        if collection is not None:
            return Database.DATABASE[collection].find(query)
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
            return Database.DATABASE[collection].insert(data)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def update(collection, query, data):
        if collection is not None:
            return Database.DATABASE[collection].update(query, data)
        else:
            raise pymongo.errors.InvalidOperation

    @staticmethod
    def remove(collection, query):
        if collection is not None:
            return Database.DATABASE[collection].remove(query)
        else:
            raise pymongo.errors.InvalidOperation
