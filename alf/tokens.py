# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


class TokenError(Exception):

    def __init__(self, message, response):
        super(TokenError, self).__init__(message)
        self.response = response


class Token(object):

    def __init__(self, access_token='', expires_in=0):
        self._access_token = access_token
        self._expires_in = expires_in

        self._update_expires_on()

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token

    def is_valid(self):
        return self._expires_on >= datetime.now()

    @property
    def expires_in(self):
        return self._expires_in

    @expires_in.setter
    def expires_in(self, expires_in):
        self._expires_in = expires_in

        self._update_expires_on()

    def _update_expires_on(self):
        self._expires_on = datetime.now() + timedelta(seconds=self.expires_in)
