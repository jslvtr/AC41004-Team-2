import datetime
import uuid
from unittest import TestCase
from src.app import get_db
from src.common.database import Database
from src.models.event import Event
from src.models.permissions import Permissions
from src.models.eventregister import EventRegister

__author__ = 'jamie'


class TestEventRegister(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def test_event_register(self):
        user = "Jamie"
        event = Event(title="Test event",
                      description="Test description",
                      start=datetime.datetime.utcnow().strftime('%m/%d/%Y %I:%M %p'),
                      end=(datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p'),
                      event_type="action",
                      points=10)
        event.save_to_db()

        EventRegister.register_for_event(user, event.get_id())

        self.assertIsNotNone(EventRegister.check_if_registered(user, event.get_id()))

        Database.remove("registrations", {"user": user, "event": event.get_id()})
        Database.remove(Event.COLLECTION, {'_id': event.get_id()})

    def test_event_unregister(self):
        user = "Jamie"
        event = Event(title="Test event",
                      description="Test description",
                      start=datetime.datetime.utcnow().strftime('%m/%d/%Y %I:%M %p'),
                      end=(datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p'),
                      event_type="action",
                      points=10)
        event.save_to_db()

        EventRegister.register_for_event(user, event.get_id())

        EventRegister.unregister_for_event(user, event.get_id())

        self.assertIsNone(EventRegister.check_if_registered(user, event.get_id()))

        Database.remove(Event.COLLECTION, {'_id': event.get_id()})

    def test_user_attended(self):
        user = "Jamie"
        event = Event(title="Test event",
                      description="Test description",
                      start=datetime.datetime.utcnow().strftime('%m/%d/%Y %I:%M %p'),
                      end=(datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime('%m/%d/%Y %I:%M %p'),
                      event_type="action",
                      points=10)
        event.save_to_db()

        EventRegister.register_for_event(user, event.get_id())

        EventRegister.set_user_attended(user, event.get_id().hex)

        self.assertEquals(EventRegister.get_user_attended(user, event.get_id().hex), True)

        EventRegister.set_user_attended(user, event.get_id().hex)

        self.assertEquals(EventRegister.get_user_attended(user, event.get_id().hex), False)

        Database.remove(Event.COLLECTION, {'_id': event.get_id()})
