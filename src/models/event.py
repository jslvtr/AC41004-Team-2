from src.common.database import Database
import uuid
from datetime import datetime

__author__ = 'stamas01'



class NoSuchEventExistException(Exception):
    def __init__(self):
        self.message = "No such event exists"

    def __str__(self):
        return repr(self.message)


class Event:
    def __init__(self, title, description, date, id_=None):
        self.__title = title
        self.__description = description
        self.__date = date
        self.__id = id_
        self.__synced = False

    def get_title(self):
        return self.__title

    def set_title(self,title):
        self.__title = title
        self.__synced = False

    def get_description(self):
        return self.__description

    def get_id(self):
        return self.__id

    def set_description(self, description):
        self.__description = description
        self.__synced = False

    @classmethod
    def get_by_title(cls, title):
        event = Database.find_one('events',{'title': title})
        return Event.factory_form_json(event)

    @classmethod
    def get_by_id(cls, id_):
        event = Database.find_one('events', {'_id': id_})
        return Event.factory_form_json(event)

    @classmethod
    def factory_form_json(cls, event_json):
        if event_json is None:
            raise NoSuchEventExistException()
        event_obj = cls(event_json['title'], event_json['description'], event_json['date'], event_json['_id']);
        event_obj.__synced = True
        return event_obj

    def save_to_db(self):
        if self.__id is None:
            self.__id = uuid.uuid4()
            Database.insert('events',self.to_json())

    def remove_from_db(self):
        Database.remove('events', {'_id': self.__id})


    def is_synced(self):
        return self.__synced

    def is_valid_model(self):
        if type(self.__title) is not str:
            return False
        if type(self.__description) is not str:
            return False
        #if type(self.__id) is not uuid.UUID and not None:
            #return False
        if type(self.__date) is not datetime:
            return False
        return True

    def sync_to_db(self):
        if self.__synced is False:
            self.__synced = True
            Database.update('events', {'_id': self.__id}, {'title': self.__title, 'description': self.__description, 'date': self.__date})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_title() == other.get_title() and
                    self.get_description() == other.get_description())

    def to_json(self):
        return {'title': self.__title, 'description': self.__description, 'date': self.__date, '_id': self.__id}


