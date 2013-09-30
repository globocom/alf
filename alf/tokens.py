# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


class TokenError(Exception):

    def __init__(self, message, response):
        super(TokenError, self).__init__(message)
        self.response = response


class Token(object):

    def __init__(self, access_token='', expires_in=0):
        self.access_token = access_token
        self._expires_in = expires_in

        self._expires_on = datetime.now() + timedelta(seconds=self._expires_in)

    def is_valid(self):
        return self._expires_on > datetime.now()
