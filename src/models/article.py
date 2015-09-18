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
        self.__title = title
        self.__summary = summary
        self.__date = date
        self.__id = id_
        self.__synced = False

    def get_title(self):
        return self.__title

    def set_title(self,title):
        self.__title = title
        self.__synced = False

    def get_summary(self):
        return self.__summary

    def get_id(self):
        return self.__id

    def set_summary(self, summary):
        self.__summary = summary
        self.__synced = False

    @classmethod
    def get_by_title(cls, title):
        article = Database.find_one('articles',{'title': title})
        return Article.factory_form_json(article)

    @classmethod
    def get_by_id(cls, id_):
        article = Database.find_one('articles', {'_id': id_})
        return Article.factory_form_json(article)

    @classmethod
    def factory_form_json(cls, article_json):
        if article_json is None:
            raise NoSuchArticleExistException()
        article_obj = cls(article_json['title'], article_json['summary'], article_json['date'], article_json['_id']);
        article_obj.__synced = True
        return article_obj

    def save_to_db(self):
        if self.__id is None:
            self.__id = uuid.uuid4()
            Database.insert('articles',self.to_json())

    def remove_from_db(self):
        Database.remove('articles', {'_id': self.__id})

    def is_synced(self):
        return self.__synced

    def is_valid_model(self):
        if type(self.__title) is not str:
            return False
        if type(self.__summary) is not str:
            return False
        #if type(self.__id) is not uuid.UUID and not None:
            #return False
        if type(self.__date) is not datetime:
            return False
        return True

    def sync_to_db(self):
        if self.__synced is False:
            self.__synced = True
            Database.update('articles', {'_id': self.__id}, {'title': self.__title, 'summary': self.__summary, 'date': self.__date})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_title() == other.get_title() and
                    self.get_summary() == other.get_summary())

    def to_json(self):
        return {'title': self.__title, 'summary': self.__summary, 'date': self.__date, '_id': self.__id}


