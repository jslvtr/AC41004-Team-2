import time
from src.common.database import Database
from src.models.event import Event

__author__ = 'jamie'


class EventRegister(object):

        @staticmethod
        def register_for_event(user, event):
            event_to_use = Event.get_by_id(event)
            Database.insert("registrations", {"user": user, "event": event,"title": event_to_use.get_title(),
                                              "date": time.strftime("%d/%m/%Y"), "attended": "No"})

        @staticmethod
        def check_if_registered(user, event):
            return Database.find_one("registrations", {"user": user, "event": event})

        @staticmethod
        def unregister_for_event(user, event):
            Database.remove("registrations", {"user": user, "event": event})

        @staticmethod
        def set_user_attended(user, event):
            Database.update("registrations", {"user": user, "event": event}, {"attended": "Yes"}, upsert=True)