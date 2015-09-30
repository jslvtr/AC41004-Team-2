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


class QuizProfile:

    COLLECTION = "quiz_profile"

    def __init__(self, quiz_id, user_id, last_try, try_number,  passed):
        self._quiz_id = quiz_id
        self._user_id = user_id
        self._last_try = last_try
        self._try_number = try_number
        self._passed = passed

    def get_quiz_id(self):
        return self._quiz_id

    def set_quiz_id(self, quiz_id):
        self._quiz_id = quiz_id

    def get_try_number(self):
        return self._quiz_id

    def set_try_number(self, try_number):
        self._try_number = try_number

    def get_last_try(self):
        return self._last_try

    def set_quiz_id(self, last_try):
        self._last_try = last_try

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
    def get_by_user(cls, user_id):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'user_id': user_id})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def get_by_composite_id(cls, quiz_id, user_id):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'user_id': user_id, 'quiz_id': quiz_id})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def factory_form_json(cls, quiz_profile_json):
        if quiz_profile_json is None:
            raise NoSuchQuizProfileExistException()
        quiz_profile_obj = cls(quiz_profile_json['quiz_id'], quiz_profile_json['user_id'],  quiz_profile_json['last_try'], quiz_profile_json['try_number'], quiz_profile_json['passed'])
        return quiz_profile_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert(self.COLLECTION, self.to_json())

    def remove_from_db(self):
        Database.remove(self.COLLECTION, {'quiz_id': self._quiz_id })

    def is_valid_model(self):
        if not isinstance(self._quiz_id, uuid.UUID):
            return False
        if not isinstance(self._passed, bool):
            return False
        return True

    def sync_to_db(self):
        if self._synced is False:
            Database.update(self.COLLECTION,
                            {'quiz_id': self._id, 'user_id': self._id},
                            {'passed': self._passed,
                             'try_number': self._try_number,
                             'last_try': self._last_try,})

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_quiz_id() == other.get_quiz_id() and
                    self.get_user_id() == other.get_user_id() and
                    self.get_last_try() == other.get_last_try() and
                    self.get_try_number() == other.get_try_number())

    def to_json(self):
        return {'user_id': self._user_id,
                'quiz_id': self._quiz_id,
                'last_try': self._last_try,
                'try_number': self._try_number,
                'passed': self._passed}
