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
    def get_college(university, college_to_find):
        uni = Database.find_one(COLLECTION, {"name": university, "colleges.name": college_to_find})
        colleges = [college for college in uni['colleges']]
        for college in colleges:
            if college_to_find == college['name']:
                return college
            else:
                return False


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
        if Database.update(COLLECTION, {"name": university}, {"$addToSet": {"colleges": {"name": college}}},
                                upsert=True):
            return True
        return False

    @staticmethod
    def add_course(university, college, course):
        if Database.update(COLLECTION, {"name": university, "colleges.name": college},
                           {"$addToSet": {'colleges.$.courses': course}}):
            return True
        return False

    @staticmethod
    def delete_university(university):
        if Database.remove("universities", {"name": university}):
            return True
        return False

    @staticmethod
    def delete_college(university, college):
        if Database.update(COLLECTION, {"name": university}, {"$pull": {"colleges": {"name": college}}}):
            return True
        return False

    @staticmethod
    def delete_course(university, college, course):
        if Database.update(COLLECTION, {"name": university, "colleges.name": college},
                           {"$pull": {'colleges.$.courses': course}}):
            return True
        return False
