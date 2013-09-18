# -*- coding: utf-8 -*-
import requests
from alf.tokens import Token, TokenDjango, TokenError


class TokenManager(object):

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

        if not response.ok:
            raise TokenError('Failed to request token', response)

        token_data = response.json()

        self._token.access_token = token_data.get('access_token', '')
        self._token.expires_in = token_data.get('expires_in', 0)


class TokenManagerDjango(TokenManager):

    def __init__(self, *args, **kwargs):
        super(TokenManagerDjango, self).__init__(*args, **kwargs)

        self._token = TokenDjango()
