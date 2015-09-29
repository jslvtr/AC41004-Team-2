import time
import uuid
from src.common.database import Database
from src.models.event import Event

__author__ = 'jamie'


class EventRegister(object):

        @staticmethod
        def register_for_event(user, event):
            event_to_use = Event.get_by_id(event)
            Database.insert("registrations", {"user": user, "event": event, "title": event_to_use.get_title(),
                                              "date": time.strftime("%d/%m/%Y"), "attended": "No"})

        @staticmethod
        def check_if_registered(user, event):
            return Database.find_one("registrations", {"user": user, "event": event})

        @staticmethod
        def unregister_for_event(user, event):
            Database.remove("registrations", {"user": user, "event": event})

        @staticmethod
        def set_user_attended(user, event):
            if EventRegister.get_user_attended(user, event):
                Database.update("registrations", {"user": user, "event": uuid.UUID(event)}, {"$set": {"attended": "No"}},
                                upsert=True)
            else:
                Database.update("registrations", {"user": user, "event": uuid.UUID(event)}, {"$set": {"attended": "Yes"}},
                                upsert=True)

        @staticmethod
        def get_user_attended(user, event):
            if Database.find_one("registrations", {"user": user, "event": uuid.UUID(event), "attended": "Yes"}):
                return True
            else:
                return False




        @staticmethod
        def list_registered_users(event):
            return Database.find("registrations", {"event": event})
