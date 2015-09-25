from src.common.constants import Constants
from src.models.grid_settings import GridSettings

__author__ = 'jslvtr'

class PageContent:
    def __init__(self, title, template, content, grid_settings ):
        self._title = title;
        self._template = template;
        self._content = content;
        self._grid_settings = grid_settings;

    def get_content(self):
        return self._content

    def set_content(self,content):
        self._content = content

    def get_grid_settings(self):
        return self._grid_settings

    def set_grid_settings(self,grid_settings):
        self._content = grid_settings

    def get_template(self):
        return self._template

    def set_template(self,template):
        self._template = template

    def get_title(self):
        return self.title

    def set_title(self,title):
        self._title = title

    def is_valid_model(self):
        if type(self._template) is not str:
            return False
        if next((x for x in Constants.TEMPLATES if x.name == self._template), None) is None:
            return False
        if not isinstance(self._grid_settings, GridSettings):
            return False
        if not self._grid_settings.is_valid_model():
            return False
        if type(self._content) is not str:
            return False
        if type(self._title) is not str:
            return False
        return True

    def factory_form_json(cls, json):
        obj = cls(json['title'], json['template'], json['content'], GridSettings.factory_form_json(json['grid_settings']))
        return obj

    def to_json(self):
        return {'title': self._title, 'template': self._template, 'content': self._content, 'grid_settings': self._grid_settings.to_json()}