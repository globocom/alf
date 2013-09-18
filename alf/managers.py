# -*- coding: utf-8 -*-

import requests
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

    def set_expires_in(self, expires_in):
        self._expires_in = expires_in

        self._update_expires_on()

    def _update_expires_on(self):
        self._expires_on = datetime.now() + timedelta(seconds=self._expires_in)


class DjangoCachedToken(Token):

    @property
    def access_token(self):
        pass

    @access_token.setter
    def access_token(self, access_token):
        pass

    def is_valid(self):
        pass


class SimpleTokenManager(object):

    def __init__(self, token_endpoint, client_id, client_secret):
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        self._token = Token()

    def has_token(self):
        return self._token.is_valid()

    def get_token(self):
        return self._token._access_token

    def request_token(self):
        response = requests.post(
            self._token_endpoint,
            data={'grant_type': 'client_credentials'},
            auth=(self._client_id, self._client_secret))

        if not response.ok:
            raise TokenError('Failed to request token', response)

        token_data = response.json()
        #self._token = Token(
            #token_data.get('access_token', ''),
            #token_data.get('expires_in', 0))

        self._token.set_access_token(token_data.get('access_token', ''))
        self.set_expires_in(token_data.get('expires_in', ''))


class DjangoTokenManager(SimpleTokenManager):

    def __init__(self, *args, **kwargs):
        super(DjangoTokenManager, self).__init__(args, kwargs)

        self._token = DjangoCachedToken()
