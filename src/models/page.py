import uuid
from src.common.database import Database
from src.common.utils import Utils
from src.models.article import Article

_author_ = 'stamas01'


class NoSuchPageExistException(Exception):
    def __init__(self):
        self.message = "No such page exists"

    def __str__(self):
        return repr(self.message)


class PageAlreadyExistException(Exception):
    def __init__(self):
        self.message = "A page with this name already exists"

    def __str__(self):
        return repr(self.message)


class Page:
    COLLECTION = "pages"

    def __init__(self, title, content, feed=False, active=False, id=None):
        self._content = content
        self._title = title
        self._id = id
        self._feed = feed
        self._active = active

    def get_id(self):
        return self._id

    def get_content(self):
        return self._content

    def set_content(self,content):
        self._content = content

    def get_title(self):
        return self._title

    def set_title(self,title):
        self._title = title

    def get_feed(self):
        return self._feed

    def set_feed(self,feed):
        self._feed = feed

    def get_active(self):
        return self._active

    def set_active(self,active):
        self._active = active

    def remove_from_db(self):
        if self._feed:
            news = [article for article in Database.find("articles", {"page_id" : uuid.UUID('{00000000-0000-0000-0000-000000000000}')})]
            for article in news:
                article = Article.get_by_id(article['_id'])
                article.remove_from_db()
        Database.remove(self.COLLECTION, {'_id': self._id})

    def is_valid_model(self):
        if not isinstance(self._title,str):
            return False
        if not isinstance(self._content,str):
            return False
        if not isinstance(self._feed,bool):
            return False
        if not isinstance(self._active,bool):
            return False
        return True

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
        Database.insert(self.COLLECTION, self.to_json())

    def is_there_any_with_title(self,title):
        article = Database.find_one(self.COLLECTION, {'title': title})
        return article is not None

    def sync_to_db(self):
        Database.update(self.COLLECTION,
                        {'_id': self._id},
                        {'title': self._title, 'content': self._content, 'feed': self._feed, 'active': self._active})

    @classmethod
    def get_all(cls):
        pages  = Database.find(cls.COLLECTION,{})
        result = []
        for page in pages:
            result.append(Page.factory_form_json(page))
        return result

    @classmethod
    def get_by_title(cls, title):
        page = Database.find_one(cls.COLLECTION, {'title': title})
        return Page.factory_form_json(page)


    @classmethod
    def get_by_id(cls, id_):
        page = Database.find_one(cls.COLLECTION, {'_id': id_})
        return Page.factory_form_json(page)

    @classmethod
    def factory_form_json(cls, json):
        if json is None:
            raise NoSuchPageExistException()
        obj = cls(json['title'], json['content'], json['feed'], json['active'], json['_id'])
        return obj

    def to_json(self):
        return {'title': self._title, 'content': self._content, 'feed': self._feed, 'active': self._active, '_id': self._id}
