import time
from src.common.database import Database

__author__ = 'jamie'


class EventRegister(object):

        @staticmethod
        def register_for_event(user,event):
            Database.insert("registrations", {"user": user, "event": event, "date": time.strftime("%d/%m/%Y")})

        @staticmethod
        def check_if_registered(user, event):
            return Database.find_one("registrations", {"user": user, "event": event})

        @staticmethod
        def unregister_for_event(user, event):
            Database.remove("registrations", {"user": user, "event":event})