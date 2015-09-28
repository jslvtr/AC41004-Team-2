from src.common.database import Database
import uuid
from datetime import datetime
from src.models.quiz_answer import QuizAnswer
from src.models.quiz_question import QuizQuestion

__author__ = 'stamas01'


class NoSuchQuizExistException(Exception):
    def __init__(self):
        self.message = "No such quiz question exists"

    def __str__(self):
        return repr(self.message)


class Quiz:

    COLLECTION = "quiz"

    def __init__(self, title, questions, points, id_=None):
        self._title = title
        self._questions = questions
        self._points = points
        self._id = id_

    def get_title(self):
        return self._title

    def set_title(self, title):
        self._questions = title

    def get_questions(self):
        return self._questions

    def set_questions(self, questions):
        self._questions = questions

    def get_points(self):
        return self._points

    def set_points(self, points):
        self._points = points

    @classmethod
    def get_all(cls, id_):
        quizzez_json = Database.find_one(QuizQuestion.COLLECTION, {})
        quizzez = []
        for quiz in quizzez_json:
            quizzez.append(quiz.factory_form_json())
        return quizzez

    @classmethod
    def get_by_id(cls, id_):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'_id': id_})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def factory_form_json(cls, quiz_json):
        if quiz_json is None:
            raise NoSuchQuizExistException()
        questions = []
        for question in quiz_json['questions']:
            questions.append(QuizQuestion.factory_form_json(question))
            
        quiz_obj = cls(questions, quiz_json['points'])
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
