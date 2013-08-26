# -*- coding: utf-8 -*-

from mock import patch
from unittest import TestCase

from alf.managers import SimpleTokenManager, Token


class TestSimpleTokenManager(TestCase):

    def setUp(self):
        self.end_point = 'http://endpoint/token'
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'

        self.manager = SimpleTokenManager(
            self.end_point, self.client_id, self.client_secret)

    def test_should_start_with_no_token(self):
        self.assertFalse(self.manager.has_token())

    def test_should_detect_expired_token(self):
        self.manager._token = Token('', expires_in=0)
        self.assertFalse(self.manager.has_token())

    def test_should_respect_valid_token(self):
        self.manager._token = Token('', expires_in=10)
        self.assertTrue(self.manager.has_token())

    @patch('requests.post')
    def test_should_be_able_to_request_a_new_token(self, post):
        post.return_value.json.return_value = {
            'access_token': 'accesstoken',
            'expires_in': 10,
        }

        self.manager.request_token()

        self.assertTrue(self.manager.has_token())
        post.assert_called_with(
            self.end_point,
            data={'grant_type': 'client_credentials'},
            auth=(self.client_id, self.client_secret))
