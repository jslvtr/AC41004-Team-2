from unittest import TestCase
from src.app import get_db
from src.common.database import Database
from src.models.permissions import Permissions
from src.models.eventregister import EventRegister

__author__ = 'jamie'

class TestEventRegister(TestCase):

    @classmethod
    def setUpClass(cls):
        get_db()

    def test_event_register(self):

        user = "Jamie"
        event_id = "123456"

        EventRegister.register_for_event(user, event_id)

        self.assertIsNotNone(EventRegister.check_if_registered(user, event_id))

        Database.remove("registrations", {"user": user, "event": event_id})

    def test_event_unregister(self):

        user = "Jamie"
        event_id = "123456"

        EventRegister.register_for_event(user, event_id)

        EventRegister.unregister_for_event(user, event_id)

        self.assertIsNone(EventRegister.check_if_registered(user, event_id))
