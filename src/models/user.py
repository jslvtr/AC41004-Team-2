from _sha256 import sha256
from src.common.database import Database

__author__ = 'jslvtr'


class User(object):
    def __init__(self):
        pass

    @staticmethod
    def check_login(email, password):
        # This method checks a login/password combo is correct
        document = Database.find_one('users', {"email": email})
        if document is not None:
            password_encode = password.encode('utf-8')
            if document['password'] == sha256(password_encode).hexdigest():
                return True
        return False

    @staticmethod
    def register_user(email, password):
        # This method will add a new user to the database
        if Database.find_one("users", {"email": email}):
            # This user already exists
            return False
        encrypted_password = sha256(password.encode('utf-8'))
        Database.insert("users", {"email": email, "password": encrypted_password.hexdigest()})
        return True

    @staticmethod
    def get_user_profile(user):
        # This method will get the user profile of the currently logged in user
        return Database.find_one("users", {"email": user})


