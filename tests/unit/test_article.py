from unittest import TestCase
import uuid
from src.common.database import Database
from src.models.article import Article, NoSuchArticleExistException
from datetime import datetime
import os

__author__ = 'stamas01'

mongodb_user = os.environ.get("MONGODB_USER")
mongodb_password = os.environ.get("MONGODB_PASSWORD")
mongo_url = os.environ.get("MONGODB_URL")
mongo_port = os.environ.get("MONGODB_PORT")
mongo_database = os.environ.get("MONGODB_DATABASE")


class TestArticle(TestCase):

    def setUp(self):
        Database.initialize(mongodb_user, mongodb_password, mongo_url, int(mongo_port), mongo_database)

    def test_factory_form_json(self):
        article = Article("Test", "lk", datetime.now())
        self.assertEqual(article, Article.factory_form_json(article.to_json()), "Creating article object from json failed")

    def test_save_to_db(self):
        article = Article("Test", "lk", datetime.now())
        article.save_to_db()
        try:
            test_result = Article.get_by_id(article.get_id())
        except NoSuchArticleExistException:
            self.fail()
        article.remove_from_db()
        self.assertEqual(test_result, article, "Saved and retrieved article is not the same")

    def test_remove_from_db(self):
        article = Article("Test", "lk", datetime.now())
        article.save_to_db()
        try:
            article.remove_from_db()
        except NoSuchArticleExistException:
            self.fail("Error occurred when tried to delete existing article")

    def test_remove_non_existing_event_from_db(self):
        article = Article("Test", "lk", datetime.now(), uuid.uuid4())
        self.assertRaises(NoSuchArticleExistException,article.remove_from_db())

    def test_not_synced(self):
        article = Article("Test", "lk", datetime.now())
        article.save_to_db()
        article.set_title("TestUpdated")
        self.assertFalse(article.is_synced(),"article marked synced when it is not")
        article.remove_from_db()

    def test_is_synced(self):
        article = Article("Test", "lk", datetime.now())
        article.save_to_db()
        article.set_title("TestUpdated")
        article.sync_to_db()
        self.assertTrue(article.is_synced(), "article marked un-synced when it is")
        article.remove_from_db()

    def test_is_valid_model(self):
        article = Article("Test", "lk", datetime.now(),uuid.uuid4())
        self.assertTrue(article.is_valid_model(),"Valid model is invalid")

    def test_is_not_valid_model(self):
        article = Article(12, 12, "hello","sd")
        self.assertFalse(article.is_valid_model(),"Invalid model is valid")

    def test_sync_to_db(self):
        article = Article("Test", "lk", datetime.now())
        article.save_to_db()
        article.set_title("TestUpdated")
        article.sync_to_db()
        try:
            test_result = Article.get_by_id(article.get_id())
        except NoSuchArticleExistException:
            self.fail()
        article.remove_from_db()
        self.assertEqual(test_result, article, "Sync event with database failed")

    def test_to_json(self):
        dt = datetime.now()
        id_ = uuid.uuid4()
        article = Article("Test", "lk", dt,id_)
        self.equal = self.assertEqual(article.to_json(), {'title': 'Test', 'summary': 'lk', 'date': dt, '_id': id_})
