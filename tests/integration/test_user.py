from unittest import TestCase
from src.app import get_db
from src.common.database import Database
from src.models.permissions import Permissions
from src.models.user import User

__author__ = 'jslvtr'


class TestUser(TestCase):

    @classmethod
    def setUpClass(cls):
        get_db()

    def test_user_creation(self):
        user = User("test@example.com", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

        self.assertIsNotNone(user)

    def test_save_simple_user_to_db(self):
        email = "test@example.com"
        user = User(email, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        user.permissions = Permissions.default()
        user.save_to_db()

        self.assertIsNotNone(User.find_by_email(email))

        Database.remove("users", {"email": email})

    def test_save_complex_user_to_db(self):
        email = "test@example.com"
        encrypted_password = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        country = "Spain"
        university = "Abertay"

        user = User(email, encrypted_password)
        user.data['country'] = country
        user.data['university'] = university
        user.permissions = Permissions.default()
        user.save_to_db()

        user_from_db = User.find_by_email(email)

        self.assertEqual(user_from_db.email, email)
        self.assertEqual(user_from_db.encrypted_password, encrypted_password)
        self.assertEqual(user_from_db.data['country'], country)
        self.assertEqual(user_from_db.data['university'], university)

        Database.remove("users", {"email": email})

    def test_user_json(self):
        email = "test@example.com"
        encrypted_password = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        country = "Spain"
        university = "Abertay"

        user = User(email, encrypted_password)
        user.permissions = Permissions.default()
        user.data['country'] = country
        user.data['university'] = university

        self.assertEqual(user.json(),
                         {
                             "email": email,
                             "password": encrypted_password,
                             "country": country,
                             "university": university,
                             "permissions": "user"
                         })