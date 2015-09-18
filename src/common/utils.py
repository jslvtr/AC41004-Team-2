__author__ = 'jslvtr'

import re


class Utils(object):

    @staticmethod
    def email_is_valid(email):
        address = re.compile('^[\w\d.+-]+@([\w\d.]+\.)+[\w]+$')
        return True if address.match(email) else False
