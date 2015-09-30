from src.common.database import Database
import uuid
from datetime import datetime

__author__ = 'stamas01'

class QuizAnswer:

    COLLECTION = "quiz"

    def __init__(self, answer_text, correct):
        self._answer_text = answer_text
        self._correct = correct

    def get_answer_text(self):
        return self._answer_text

    def set_answer_text(self, answer_text):
        self._answer_text = answer_text

    def get_correct(self):
        return self._correct

    def set_correct(self, correct):
        self._correct = correct

    @classmethod
    def factory_form_json(cls, answer_json):
        answer_obj = cls(answer_json['answer_text'], answer_json['correct'])
        return answer_obj

    def is_synced(self):
        return self._synced

    def is_valid_model(self):
        if type(self._answer_text) is not str:
            return False
        if type(self._correct) is not bool:
            return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.get_answer_text() == other.get_answer_text() and
                    self.get_correct() == other.get_correct())

    def to_json(self):
        return {'answer_text': self._answer_text, 'correct': self._correct}
