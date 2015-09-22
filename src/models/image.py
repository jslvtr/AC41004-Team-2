from src.common.database import Database
import uuid
from datetime import datetime

_author_ = 'stamas01'





class Image:
    def __init__(self, data, id_=None):
        self._data = data
        self._id = id_

    def set_data(self,data):
        self._data = data

    def get_data(self,data):
        return self._date

    def get_id(self):
        return self._id

    @classmethod
    def get_by_id(cls, id_):
        iamge = Database.find_one('images', {'_id': id_})
        return Image.factory_form_json(iamge)

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


