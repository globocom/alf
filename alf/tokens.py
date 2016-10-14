# -*- coding: utf-8 -*-
from datetime import datetime, timedelta


class TokenError(Exception):

    def __init__(self, message, response):
        super(TokenError, self).__init__(message)
        self.response = response


class Token(object):

    def __init__(self, access_token='', expires_on=0):
        self.access_token = access_token
        self.expires_on = expires_on or self.calc_expires_on()

    def is_valid(self):
        return self.expires_on > datetime.now()

    @staticmethod
    def calc_expires_on(expires_in=0):
        return datetime.now() + timedelta(seconds=int(expires_in))


class TokenStorage(object):

    TOKEN_EXPIRES_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, custom_storage=None, base_key=None):
        self._access_token = ''
        self._expires_on = ''
        self._base_key = str(base_key)
        self._storage = custom_storage or TokenDefaultStorage()

    @property
    def token_key(self):
        return "{}_{}".format(self._base_key, 'access_token')

    @property
    def expires_key(self):
        return "{}_{}".format(self._base_key, 'expires_on')

    def __call__(self, token):
        if token.access_token != self._access_token \
                or token.expires_on != self._expires_on:
            self._access_token = token.access_token
            self._expires_on = token.expires_on
            self._storage.set(self.token_key, token.access_token)
            self._storage.set(
                self.expires_key,
                token.expires_on.strftime(self.TOKEN_EXPIRES_FORMAT)
            )

    def request_token(self):
        self._access_token = self._storage.get(self.token_key)
        expires_on = self._storage.get(self.expires_key)
        if expires_on:
            self._expires_on = datetime.strptime(expires_on,
                                                 self.TOKEN_EXPIRES_FORMAT)
        else:
            self._expires_on = datetime.now()
        if self._access_token and self._expires_on > datetime.now():
            return {'access_token': self._access_token,
                    'expires_on': self._expires_on}
        return dict()


class TokenDefaultStorage(object):

    def __init__(self):
        self.storage = dict()

    def get(self, key):
        return self.storage.get(key)

    def set(self, key, value):
        self.storage[key] = value
