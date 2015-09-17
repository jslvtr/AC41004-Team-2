from _sha256 import sha256
from src.common.database import Database

__author__ = 'jslvtr'


class User(object):
    def __init__(self):
        pass

    @staticmethod
    def check_login(email, password):
        # This method checks a login/password combo is correct
        document = Database.find_one("users", {"email": "test@example.com"})
        if sha256(document['password']) == password:
            return True
        return False
