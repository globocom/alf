# -*- coding: utf-8 -*-

import requests

from alf.managers import TokenManager
from alf.tokens import TokenError
from alf.auth import BearerTokenAuth


BAD_TOKEN = 401


class Client(requests.Session):

    token_manager_class = TokenManager

    def __init__(self, *args, **kwargs):
        self._token_endpoint = kwargs.pop('token_endpoint')
        self._client_id = kwargs.pop('client_id')
        self._client_secret = kwargs.pop('client_secret')
        self._token_storage = kwargs.pop('token_storage', None)
        self._token_request_params = kwargs.pop('token_request_params', None)

        _token_retries = kwargs.pop('token_retries', None)
        self._token_manager = self.token_manager_class(
            token_endpoint=self._token_endpoint,
            client_id=self._client_id,
            client_secret=self._client_secret,
            token_storage=self._token_storage,
            token_request_params=self._token_request_params,
            token_retries=_token_retries)

        super(Client, self).__init__(*args, **kwargs)

    def _request(self, *args, **kwargs):
        access_token = self._token_manager.get_token()
        kwargs['auth'] = BearerTokenAuth(access_token)
        return super(Client, self).request(*args, **kwargs)

    def request(self, *args, **kwargs):
        try:
            response = self._request(*args, **kwargs)
            if response.status_code != BAD_TOKEN:
                return response

            self._token_manager.reset_token()
            return self._request(*args, **kwargs)
        except TokenError as error:
            self._token_manager.reset_token()
            return error.response
