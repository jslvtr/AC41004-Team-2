from unittest import TestCase
import uuid
from src.common.database import Database
from src.models.event import Event, NoSuchEventExistException
from datetime import datetime
import os

__author__ = 'stamas01'

mongodb_user = os.environ.get("MONGODB_USER")
mongodb_password = os.environ.get("MONGODB_PASSWORD")
mongo_url = os.environ.get("MONGODB_URL")
mongo_port = os.environ.get("MONGODB_PORT")
mongo_database = os.environ.get("MONGODB_DATABASE")

class TestEvent(TestCase):
  def setUp(self):
        Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)

  def test_factory_form_json(self):
    event = Event("Test", "lk", datetime.now())
    self.assertEqual(event, Event.factory_form_json(event.to_json()), "Creating event object from json failed")

  def test_save_to_db(self):
    event = Event("Test", "lk", datetime.now())
    event.save_to_db()
    try:
      test_result = Event.get_by_id(event.get_id())
    except NoSuchEventExistException:
      self.fail()
    event.remove_from_db()
    self.assertEqual(test_result, event, "Saved and retrieved event is not the same")

  def test_remove_from_db(self):
    event = Event("Test", "lk", datetime.now())
    event.save_to_db()
    try:
        event.remove_from_db()
    except NoSuchEventExistException:
        self.fail("Error occurred when tried to delete existing event")

  def test_remove_non_existing_event_from_db(self):
    event = Event("Test", "lk", datetime.now(), uuid.uuid4())
    self.assertRaises(NoSuchEventExistException,event.remove_from_db())

  def test_not_synced(self):
    event = Event("Test", "lk", datetime.now())
    event.save_to_db()
    event.set_title("TestUpdated")
    self.assertFalse(event.is_synced(),"event marked synced when it is not")
    event.remove_from_db()

  def test_is_synced(self):
    event = Event("Test", "lk", datetime.now())
    event.save_to_db()
    event.set_title("TestUpdated")
    event.sync_to_db()
    self.assertTrue(event.is_synced(), "event marked un-synced when it is")
    event.remove_from_db()

  def test_is_valid_model(self):
    event = Event("Test", "lk", datetime.now(),uuid.uuid4())
    self.assertTrue(event.is_valid_model(),"Valid model is invalid")

  def test_is_not_valid_model(self):
    event = Event(12, 12, "hello","sd")
    self.assertFalse(event.is_valid_model(),"Invalid model is valid")

  def test_sync_to_db(self):
    event = Event("Test", "lk", datetime.now())
    event.save_to_db()
    event.set_title("TestUpdated")
    event.sync_to_db()
    try:
      test_result = Event.get_by_id(event.get_id())
    except NoSuchEventExistException:
      self.fail()
    event.remove_from_db()
    self.assertEqual(test_result, event, "Sync event with database failed")

  def test_to_json(self):
    dt = datetime.now()
    id_ = uuid.uuid4()
    event = Event("Test", "lk", dt,id_)
    self.equal = self.assertEqual(event.to_json(), {'title': 'Test', 'description': 'lk', 'date': dt, '_id': id_})
