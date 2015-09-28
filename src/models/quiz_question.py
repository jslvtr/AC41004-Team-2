from src.common.database import Database
import uuid
from datetime import datetime
from src.models.quiz_answer import QuizAnswer

__author__ = 'stamas01'


class NoSuchQuizQuestionExistException(Exception):
    def __init__(self):
        self.message = "No such quiz question exists"

    def __str__(self):
        return repr(self.message)


class QuizQuestion:

    COLLECTION = "quiz"

    def __init__(self, question, answers, id_=None):
        self._question = question
        self._answers = answers
        self._id = id_

    def get_id(self):
        return self._get_id

    def get_question(self):
        return self._question

    def set_question(self, question):
        self._question = question

    def get_answers(self):
        return self._answers

    def set_publication(self, answers):
        self._answers = answers

    @classmethod
    def get_by_id(cls, id_):
        quiz_question = Database.find_one(QuizQuestion.COLLECTION, {'_id': id_})
        return QuizQuestion.factory_form_json(quiz_question)

    @classmethod
    def factory_form_json(cls, quiz_question_json):
        if quiz_question_json is None:
            raise NoSuchQuizQuestionExistException()
        answers = []
        for answer in quiz_question_json['answers']:
            answers.append(QuizAnswer.factory_form_json(answer))

        quiz_question_obj = cls(quiz_question_json['question'], quiz_question_json['answers'], quiz_question_json['_id'])
        return quiz_question_obj

    def save_to_db(self):
        if self._id is None:
            self._id = uuid.uuid4()
            Database.insert('articles', self.to_json())

    def remove_from_db(self):
        Database.remove('articles', {'_id': self._id})

    def is_synced(self):
        return self._synced

    def is_valid_model(self):
        if type(self._title) is not str:
            return False
        if type(self._summary) is not str:
            return False
        if type(self._publication) is not str and self._publication is not None:
            return False
        if not isinstance(self._page_id, uuid.UUID):
            return False
        if type(self._date) is not datetime:
            return False
        return True

    def sync_to_db(self):
        if self._synced is False:
            self._synced = True
            Database.update('articles',
                            {'_id': self._id},
                            {'title': self._title,
                             'summary': self._summary,
                             'page_id': self._page_id,
                             'publication': self._publication,
                             'date': self._date
                             })

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_answers() == other.get_answers() and
                    self.get_question() == other.get_question())

    def to_json(self):
        return {'question': self.get_question(),'answers': self._answers.to_json(), '_id': self._id}
