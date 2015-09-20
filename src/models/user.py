from hashlib import sha256
from src.common.database import Database
from src.common.utils import Utils
from src.models.permissions import Permissions

__author__ = 'jslvtr'


class User(object):
    def __init__(self, email, password, permissions=None, **kwargs):
        self.email = email
        self.encrypted_password = password
        self.permissions = permissions
        self.data = kwargs

    @classmethod
    def find_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @staticmethod
    def check_login(email, password):
        # This method checks a login/password combo is correct
        user = User.find_by_email(email)
        if user is not None:
            password_encode = password.encode('utf-8')
            if user.encrypted_password == sha256(password_encode).hexdigest():
                return True
        return False

    @staticmethod
    def register_user(email, password):
        if not Utils.email_is_valid(email):
            return False
        if User.find_by_email(email) is not None:
            return False

        encrypted_password = sha256(password.encode('utf-8'))
        User(email, encrypted_password.hexdigest(), permissions=Permissions.default()).save_to_db()
        return True

    def save_to_db(self):
        Database.update("users", {"email": self.email}, {'$set': self.json()}, upsert=True)

    def json(self):
        json = {
            "email": self.email,
            "password": self.encrypted_password,
            "permissions": self.permissions.name
        }
        json.update(self.data)

        return json

    def allowed(self, type):
        return Permissions.find_by_name(self.permissions).allowed(Permissions.access_to(type))