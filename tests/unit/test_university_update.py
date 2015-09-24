from unittest import TestCase
from src.app import get_db
from src.models.university import University

__author__ = 'jamie'


class TestUniversity(TestCase):
    @classmethod
    def setUpClass(cls):
        get_db()

    def test_university_add(self):
        university = "Test Uni"

        University.add_university(university)

        self.assertIsNotNone(University.get_uni(university))

    def test_college_add(self):
        university = "Test Uni"
        college = "Test College"

        University.add_college(university, college)

        self.assertIsNotNone(University.get_college(university, college))

    def test_course_add(self):
        university = "Test Uni"
        college = "Test College"
        course = "Test Course"

        University.add_course(university, college, course)

        self.assertIsNotNone(University.get_course(university,college,course))


