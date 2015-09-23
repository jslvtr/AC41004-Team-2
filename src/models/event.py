from src.common.database import Database
import uuid
from datetime import datetime

_author_ = 'stamas01'



class NoSuchEventExistException(Exception):
    def __init__(self):
        self.message = "No such event exists"

    def __str__(self):
        return repr(self.message)


class Event:
    def __init__(self, title, description, start, end, id_=None):
        self._title = title
        self._description = description
        self._start = start
        self._end = start
        self._id = id_
        self._synced = False

    def get_title(self):
        return self._title

    def set_title(self,title):
        self._title = title
        self._synced = False

    def get_start(self):
        return self._start

    def set_start(self,start):
        self._start = start
        self._synced = False

    def get_end(self):
        return self._end

    def set_end(self,end):
        self._end = end
        self._synced = False

    def get_description(self):
        return self._description

    def get_id(self):
        return self._id

    def set_description(self, description):
        self._description = description
        self._synced = False

    @classmethod
    def get_by_title(cls, title):
        event = Database.find_one('events', {'title': title})
        return Event.factory_form_json(event)

    @classmethod
    def get_by_id(cls, id_):
        event = Database.find_one('events', {'_id': id_})
        return Event.factory_form_json(event)

    @classmethod
    def factory_form_json(cls, event_json):
        if event_json is None:
            raise NoSuchEventExistException()
        event_obj = cls(event_json['title'], event_json['description'], event_json['start'], event_json['end'], event_json['_id'])
        event_obj._synced = True
        return event_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert('events', self.to_json())

    def remove_from_db(self):
        Database.remove('events', {'_id': self._id})

    def is_synced(self):
        return self._synced

    def is_valid_model(self):
        if type(self._title) is not str:
            return False
        if type(self._description) is not str:
            return False
        if type(self._start) is not datetime:
            return False
        if type(self._start) is not datetime:
            return False
        return True

    def sync_to_db(self):
        if self._synced is False:
            self._synced = True
            Database.update('events',
                            {'_id': self._id},
                            {'title': self._title, 'description': self._description, 'start': self._start, 'end': self._end})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_title() == other.get_title() and
                    self.get_description() == other.get_description())

    def to_json(self):
        return {'title': self._title, 'description': self._description, 'start': self._start, 'end': self._end, '_id': self._id}


