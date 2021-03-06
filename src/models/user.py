import csv
from hashlib import sha256
import uuid

from src.common.database import Database
from src.common.utils import Utils
from src.models.event import Event
from src.models.permissions import Permissions


__author__ = 'jslvtr and jkerr123'


class User(object):
    COLLECTION = "users"

    def __init__(self, email, password, permissions=None, **kwargs):
        self.email = email
        self.encrypted_password = password
        self.permissions = permissions
        self.data = kwargs

    @classmethod
    def find_by_email(cls, email):
        data = Database.find_one(cls.COLLECTION, {"email": email})
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
        user = User(email, encrypted_password.hexdigest(), permissions=Permissions.default().name)
        user.data.update({"points": {"action": 0, "practice": 0, "theory": 0, "networking": 0,
                                     "virtual": 0, "project": 0}})
        user.data.update({
            "country": "",
            "university": "",
            "school": "",
            "firstname": "",
            "lastname": "",
            "year": "",
            "level": "",
            "subject": ""
        })

        user.save_to_db()
        return True

    def total_points(self):
        total = 0
        for point_type in self.data['points']:
            total += self.data['points'][point_type]

        return total

    @staticmethod
    def get_registered_events(user):
        events_registered_for = Database.find("registrations", {"user": user})
        if events_registered_for is not None:
            events = list()
            for event in events_registered_for:
                events.append(Database.find_one("events", {"_id": event['event']}))
            return events
        return None

    @staticmethod
    def get_all_attended(user):
        events_attended = Database.find("registrations", {"user": user, "attended": "Yes"})
        if events_attended is not None:
            events = list()
            for event in events_attended:
                events.append(Database.find_one("events", {"_id": event['event']}))
            return events
        return None

    @staticmethod
    def get_user_list():
        return Database.find("users", {})

    @staticmethod
    def get_user_permissions(user):
        user = Database.find_one("users", {"email": user})
        return user['permissions']

    @staticmethod
    def get_by_id(user_id):
        user = Database.find_one("users", {"_id": user_id})
        return user

    @staticmethod
    def get_by_filtering(query):
        return Database.find("users", query)

    @staticmethod
    def export_to_csv(users):

        headings=["firstname", "lastname", "email", "university", "school", "subject", "level", "year", "country", "action", \
            "networking", "practice", "project", "theory", "virtual"]
        string = ""
        string += "firstname,lastname,email,university,school,subject,level of study,year of study,country," \
                  "action points,networking points,practice points,project points,theory points,virtual points \n"

        for user in users:
            # Headings up to points
            for i in range(0, 9):
                try:
                    string += "\"" + str(user[headings[i]]) + "\","
                except KeyError:
                    string += ","

            # Points headings
            for i in range(9, len(headings)):
                string += str(user["points"][headings[i]]) + "\",\""
            string += "\"\n"

        return string

    def save_to_db(self):
        Database.update(self.COLLECTION, {"email": self.email}, {'$set': self.json()}, upsert=True)

    def get_point_rank(self):
        users = [user for user in Database.find(self.COLLECTION, {})]
        top_points_user = 0
        for user in users:
            total_points = 0
            for key in user['points'].keys():
                total_points += user['points'][key]
            if total_points > top_points_user:
                top_points_user = total_points

        current_user_points = self.total_points()

        return 100 - (current_user_points / top_points_user * 100)

    @staticmethod
    def update_user_points(user, category, points):
        if Database.update("users", {"email": user}, {"$inc": {"points." + category: points}}, upsert=True):
            return True
        return False


    def json(self):
        json = {
            "email": self.email,
            "password": self.encrypted_password,
            "permissions": self.permissions
        }
        json.update(self.data)

        return json

    def allowed(self, type):
        return Permissions.find_by_name(self.permissions).allowed(Permissions.access_to(type))
