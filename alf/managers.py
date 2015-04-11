# -*- coding: utf-8 -*-
import requests
from alf.tokens import Token, TokenError, TokenStorage


class TokenManager(object):

    def __init__(self, token_endpoint, client_id, client_secret,
                 token_storage=None):
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_storage = TokenStorage(token_storage)

        self._token = Token()

    def _has_token(self):
        return self._token.is_valid()

    def get_token(self):
        if not self._has_token():
            self._update_token()

        return self._token.access_token

    def _get_token_data(self):
        token_data = self._token_storage.request_token()
        if not token_data:
            token_data = self._request_token()
            expires_in = token_data.get('expires_in', 0)
            token_data['expires_on'] = Token.calc_expires_on(expires_in)
        return token_data

    def reset_token(self):
        self._token = Token()
        self._token_storage(self._token)

    def _update_token(self):
        token_data = self._get_token_data()
        access_token = token_data.get('access_token', '')
        expires_on = token_data.get('expires_on', 0)
        self._token = Token(access_token,
                            expires_on)
        self._token_storage(self._token)

    def _request_token(self):
        response = requests.post(
            self._token_endpoint,
            data={'grant_type': 'client_credentials'},
            auth=(self._client_id, self._client_secret))

        if not response.ok:
            raise TokenError('Failed to request token', response)

        return response.json()
