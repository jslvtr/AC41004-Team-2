__author__ = 'jslvtr'

import re
from bs4 import BeautifulSoup


class Utils(object):

    @staticmethod
    def email_is_valid(email):
        address = re.compile('^[\w\d.+-]+@([\w\d.]+\.)+[\w]+$')
        return True if address.match(email) else False

    @staticmethod
    def clean_for_homepage(html, characters=255):
        no_images = Utils._remove_images(html)
        return Utils._limit_characters(str(no_images), characters)

    @staticmethod
    def _remove_images(html):
        soup = BeautifulSoup(html, 'html.parser')
        [s.extract() for s in soup('img')]
        return soup

    @staticmethod
    def _limit_characters(html, characters):
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = [s.extract() for s in soup('p')]
        num_characters = 0
        new_html = ""
        for paragraph in paragraphs:
            if num_characters <= characters:
                new_paragraph = ""
                for character in paragraph.text:
                    if num_characters + 1 <= characters:
                        new_paragraph += character
                        num_characters += 1
                new_html += "<p>{}</p>".format(new_paragraph)

        return new_html
