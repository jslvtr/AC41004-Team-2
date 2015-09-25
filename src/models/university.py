from src.common.database import Database


__author__ = 'jamie'

COLLECTION = "universities"


class University(object):

    @staticmethod
    def get_uni_list():
        return Database.find(COLLECTION, None)

    @staticmethod
    def get_uni(university):
        return Database.find_one(COLLECTION, {"name": university})

    @staticmethod
    def get_college(university, college):
        return Database.find_one(COLLECTION, {"name": university, "colleges.name": college})

    @staticmethod
    def get_course(university, college, course):

        return Database.find_one(COLLECTION, {"name": university, "colleges.name": college,
                                          "colleges[name][courses][name]": course})

    @staticmethod
    def add_university(university):
        if Database.insert(COLLECTION, {"name": university}):
            return True
        return False

    @staticmethod
    def add_college(university, college):
        if Database.update(COLLECTION, {"name": university}, {"$set": {"colleges.name": college}},
                                upsert=True):
            return True
        return False

    @staticmethod
    def add_course(university, college, course):
        if Database.update(COLLECTION,{"name": university, "colleges.name": college},
                           {"$set": {"colleges[name][courses][name]": course}}, upsert=True):
            return True
        return False
