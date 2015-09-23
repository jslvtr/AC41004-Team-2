from src.common.database import Database
import uuid
from datetime import datetime

_author_ = 'stamas01'


class NoSuchImageExistException(Exception):
    def __init__(self):
        self.message = "No such image exists"

    def __str__(self):
        return repr(self.message)


class Image:
    def __init__(self, data,content_type, id_=None):
        self._data = data
        self._content_type =content_type
        self._id = id_

    def set_data(self,data):
        self._data = data

    def set_content_type(self,content_type):
        self._content_type = content_type

    def get_data(self):
        return self._data

    def get_content_type(self):
        return self._content_type

    def get_id(self):
        return self._id

    @classmethod
    def get_by_id(cls, id_):
        image = Database.find_one('images', {'_id': id_})
        return Image.factory_form_json(image)

    @classmethod
    def factory_form_json(cls, image_json):
        if image_json is None:
            raise NoSuchImageExistException()
        image_obj = cls(image_json['data'], image_json['_id'])
        return image_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert('images',self.to_json())

    def remove_from_db(self):
        Database.remove('images', {'_id': self._id})

    def sync_to_db(self):
        Database.update('images', {'_id': self._id}, {'data': self._data})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_title() == other.get_title() and
                    self.get_description() == other.get_description())

    def to_json(self):
        return {'data': self._data, '_id': self._id}


