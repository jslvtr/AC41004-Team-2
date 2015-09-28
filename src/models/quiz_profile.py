from src.common.database import Database
import uuid
from datetime import datetime
from src.models.quiz_answer import QuizAnswer
from src.models.quiz_question import QuizQuestion

__author__ = 'stamas01'


class NoSuchQuizProfileExistException(Exception):
    def __init__(self):
        self.message = "No such quiz question exists"

    def __str__(self):
        return repr(self.message)


class Quiz:

    COLLECTION = "quiz"

    def __init__(self, quiz_id, user_id, passed):
        self._quiz_id = quiz_id
        self._user_id = user_id
        self._passed = passed

    def get_quiz_id(self):
        return self._quiz_id

    def set_quiz_id(self, quiz_id):
        self._quiz_id = quiz_id

    def get_user_id(self):
        return self._user_id

    def set_questions(self, user_id):
        self._user_id = user_id

    def get_passed(self):
        return self._passed

    def set_passed(self, passed):
        self._passed = passed


    @classmethod
    def get_by_quiz(cls, quiz_id):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'quiz_id': quiz_id})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def get_by_quiz(cls, user_id):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'user_id': user_id})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def factory_form_json(cls, quiz_profile_json):
        if quiz_profile_json is None:
            raise NoSuchQuizProfileExistException()
        questions = []
        quiz_obj = cls(quiz_profile_json['quiz_id'], quiz_profile_json['user_id'], quiz_profile_json['passed'])
        return quiz_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert(self.COLLECTION, self.to_json())

    def remove_from_db(self):
        Database.remove(self.COLLECTION, {'_id': self._id})


    def is_valid_model(self):
        if  isinstance(self._points, int):
            return False
        if  isinstance(self._questions, list):
            return False
        for question in self._questions:
            if not question.is_valid_model():
                return False
        return True

    def sync_to_db(self):
        if self._synced is False:
            Database.update(self.COLLECTION,
                            {'_id': self._id},
                            {'title': self._title,
                             'questions': self._questions.to_json(),
                             'points': self._points
                             })

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_id() == other.get_id() and
                    self.get_questions() == other.get_questions() and
                    self.get_points() == other.get_points())

    def to_json(self):
        return {'title': self._title, 'questions': self._questions.to_json(), 'points': self._points}
