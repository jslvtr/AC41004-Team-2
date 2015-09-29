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

    def __init__(self, question, answers):
        self._question = question
        self._answers = answers

    def get_question(self):
        return self._question

    def set_question(self, question):
        self._question = question

    def get_answers(self):
        return self._answers

    def set_answers(self, answers ):
        self._answers  = answers

    @classmethod
    def factory_form_json(cls, quiz_question_json):
        if quiz_question_json is None:
            raise NoSuchQuizQuestionExistException()
        answers = []
        if quiz_question_json['answers'] is not None:
            for answer in quiz_question_json['answers']:
                answers.append(QuizAnswer.factory_form_json(answer))

        quiz_question_obj = cls(quiz_question_json['question'], answers)
        return quiz_question_obj





    def is_valid_model(self):
        if not isinstance(self._question, str):
            return False
        if not isinstance(self._answers, list):
            return False
        for answer in self._answers:
            if not answer.is_valid_model():
                return False
        return True


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_answers() == other.get_answers() and
                    self.get_question() == other.get_question())

    def to_json(self):
        answers = []
        if self._answers is not None:
            for answer in self._answers:
                answers.append(answer.to_json())
        return {'question': self.get_question(),'answers': answers}
