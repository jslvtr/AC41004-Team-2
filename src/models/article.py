from src.common.database import Database
import uuid
from datetime import datetime

__author__ = 'stamas01'


class NoSuchArticleExistException(Exception):
    def __init__(self):
        self.message = "No such article exists"

    def __str__(self):
        return repr(self.message)


class Article:
    def __init__(self, title, summary, date, id_=None):
        self._title = title
        self._summary = summary
        self._date = date
        self._id = id_
        self._synced = False

    def get_title(self):
        return self._title

    def set_title(self,title):
        self._title = title
        self._synced = False

    def get_summary(self):
        return self._summary

    def get_id(self):
        return self._id

    def set_summary(self, summary):
        self._summary = summary
        self._synced = False

    @classmethod
    def get_by_title(cls, title):
        article = Database.find_one('articles', {'title': title})
        return Article.factory_form_json(article)

    @classmethod
    def get_by_id(cls, id_):
        article = Database.find_one('articles', {'_id': id_})
        return Article.factory_form_json(article)

    @classmethod
    def factory_form_json(cls, article_json):
        if article_json is None:
            raise NoSuchArticleExistException()
        article_obj = cls(article_json['title'], article_json['summary'], article_json['date'], article_json['_id'])
        article_obj._synced = True
        return article_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert('articles', self.to_json())

    def remove_from_db(self):
        Database.remove('articles', {'_id': self._id})

    def is_synced(self):
        return self._synced

    def is_valid_model(self):
        if type(self._title) is not str:
            return False
        if type(self._summary) is not str:
            return False
        if type(self._date) is not datetime:
            return False
        return True

    def sync_to_db(self):
        if self._synced is False:
            self._synced = True
            Database.update('articles', {'_id': self._id}, {'title': self._title, 'summary': self._summary, 'date': self._date})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_title() == other.get_title() and
                    self.get_summary() == other.get_summary())

    def to_json(self):
        return {'title': self._title, 'summary': self._summary, 'date': self._date, '_id': self._id}


