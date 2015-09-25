import uuid
from src.common.database import Database
from src.models.page_content import PageContent

_author_ = 'stamas01'



class NoSuchPageExistException(Exception):
    def __init__(self):
        self.message = "No such page exists"

    def __str__(self):
        return repr(self.message)

class Page:
    COLLECTION = "pages"

    def __init__(self, title, contents, number, id=None):
        self._contents = contents;
        self._title = title;
        self._id = id;
        self._number = number

    def get_id(self):
        return self._id

    def get_contents(self):
        return self._contents

    def set_contents(self,contents):
        self._contents = contents

    def get_title(self):
        return self._title

    def set_title(self,title):
        self._title = title

    def get_number(self):
        return self._number

    def set_number(self,number):
        self._number = number

    def is_valid_model(self):
        if type(self._title) is not str:
            return False
        if not isinstance(self._contents, list):
            return False
        if type(self._title) is not int:
            return False
        if next((x for x in self._contents if not x.is_valid_model()), False):
            return False
        return True

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
        Database.insert(self.COLLECTION, self.to_json())

    @classmethod
    def get_all(cls):
        event = Database.find_one(cls.COLLECTION, {'title': title})
        return Page.factory_form_json(event)

    @classmethod
    def get_by_title(cls, title):
        event = Database.find_one(cls.COLLECTION, {'title': title})
        return Page.factory_form_json(event)

    @classmethod
    def get_by_id(cls, id_):
        event = Database.find_one(cls.COLLECTION, {'_id': id_})
        return Page.factory_form_json(event)

    @classmethod
    def factory_form_json(cls, json):
        if json is None:
            raise NoSuchPageExistException()
        contents = []
        for content in json['contents']:
            contents.append(PageContent.factory_form_json(content));
        obj = cls(json['title'], contents, json['event_type'], json['number'], json['_id'])
        return obj

    def to_json(self):
        json_s = "["
        for content in self._contents:
            json_s+=str(content.to_json())
            json_s+=","
        json_s=json_s[:-1]
        return {'title': self._title, 'content': json_s, 'number': self._number, '_id': self._id}
