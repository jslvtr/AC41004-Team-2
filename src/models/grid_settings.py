from src.common.constants import Constants

__author__ = 'jslvtr'

class GridSettings:
    def __init__(self, size):
        self._size = size;

    def get_size(self):
        return self._size

    def set_size(self,size):
        self._size = size

    def is_valid_model(self):
        if type(self._size) is not int:
            return False
        return True

    def factory_form_json(cls, json):
        obj = cls(json['size'])
        return obj


    def to_json(self):
        return {'size': self._size}