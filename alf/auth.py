# -*- coding: utf-8 -*-

import requests


class BearerTokenAuth(requests.auth.AuthBase):

    def __init__(self, access_token):
        self._access_token = access_token

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(self._access_token)
        return request
