# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta


class Token(object):

    def __init__(self, access_token='', expires_in=0):
        self.access_token = access_token

        self._expires_in = expires_in

        self._created = datetime.now()
        self._expires_on = self._created + timedelta(seconds=expires_in)

    def is_valid(self):
        return self._expires_on >= datetime.now()


class SimpleTokenManager(object):

    def __init__(self, token_endpoint, client_id, client_secret):
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        self._token = Token()

    def has_token(self):
        return self._token.is_valid()

    def get_token(self):
        return self._token.access_token

    def request_token(self):
        response = requests.post(
            self._token_endpoint,
            data={'grant_type': 'client_credentials'},
            auth=(self._client_id, self._client_secret))

        token_data = response.json()
        self._token = Token(
            token_data['access_token'],
            token_data['expires_in'])


