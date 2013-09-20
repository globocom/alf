# -*- coding: utf-8 -*-
import requests
from alf.tokens import Token, TokenError


class TokenManager(object):

    def __init__(self, token_endpoint, client_id, client_secret):
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        self._token = Token()

    def _has_token(self):
        return self._token.is_valid()

    def get_token(self):
        if not self._has_token():
            self._update_token()

        return self._token.access_token

    def _get_token_data(self):
        token_data = self._request_token()
        return token_data

    def reset_token(self):
        self._token = Token()

    def _update_token(self):
        token_data = self._get_token_data()
        self._token = Token(token_data.get('access_token', ''),
                            token_data.get('expires_in', 0))

    def _request_token(self):
        response = requests.post(
            self._token_endpoint,
            data={'grant_type': 'client_credentials'},
            auth=(self._client_id, self._client_secret))

        if not response.ok:
            raise TokenError('Failed to request token', response)

        return response.json()
