from unittest import TestCase
from bs4 import BeautifulSoup
from src.common.utils import Utils

__author__ = 'jslvtr'


class TestUtils(TestCase):
    html = """
        <p>Hello, world!</p>
        <img src='http://path.com'/>
        <h2>Title</h2>
        <p>Another paragraph</p>
        """

    def test_remove_image(self):
        self.assertFalse('img' in str(Utils._remove_images(self.html)))

    def test_paragraphs(self):
        self.assertFalse('img' in Utils._limit_characters(self.html, 5))
        self.assertFalse('h2' in Utils._limit_characters(self.html, 5))
        self.assertFalse('Hello, world!' in Utils._limit_characters(self.html, 5))
        self.assertTrue('Hello' in Utils._limit_characters(self.html, 5))