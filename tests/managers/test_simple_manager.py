# -*- coding: utf-8 -*-

from mock import patch, Mock
from unittest import TestCase

from alf.managers import TokenManager, Token, TokenError


class TestSimpleTokenManager(TestCase):

    def setUp(self):
        self.end_point = 'http://endpoint/token'
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'

        self.manager = TokenManager(self.end_point,
                                    self.client_id,
                                    self.client_secret)

    def test_should_start_with_no_token(self):
        self.assertFalse(self.manager._has_token())

    def test_should_detect_expired_token(self):
        self.manager._token = Token('', expires_in=0)
        self.assertFalse(self.manager._has_token())

    def test_should_respect_valid_token(self):
        self.manager._token = Token('', expires_in=10)
        self.assertTrue(self.manager._has_token())

    @patch('requests.post')
    def test_should_be_able_to_request_a_new_token(self, post):
        post.return_value.json.return_value = {
            'access_token': 'accesstoken',
            'expires_in': 10,
        }

        self.manager._request_token()

        post.assert_called_with(self.end_point,
                                data={'grant_type': 'client_credentials'},
                                auth=(self.client_id, self.client_secret))

    @patch('requests.post')
    def test_should_raise_token_error_for_bad_token(self, post):
        post.return_value = Mock()
        post.return_value.ok = False
        post.return_value.status_code = 500

        with self.assertRaises(TokenError) as context:
            self.manager._request_token()

        self.assertEqual(context.exception.response.status_code, 500)

    @patch('alf.managers.TokenManager._request_token')
    def test_get_token_data_should_obtain_new_token(self, _request_token):
        self.manager._get_token_data()

        _request_token.assert_called_once()

    @patch('alf.managers.TokenManager._request_token')
    def test_update_token_should_set_a_fallback_token_in_case_of_token_retrieve_error(self, _request_token):
        _request_token.side_effect = TokenError('Message', Mock())
        self.manager._token = Token('access_token', expires_in=100)

        self.manager._update_token()

        _request_token.assert_called_once()

        self.assertEqual(self.manager._token.access_token, '')
        self.assertEqual(self.manager._token._expires_in, 0)

    @patch('alf.managers.TokenManager._request_token')
    def test_update_token_should_set_a_token_with_data_retrieved(self, _request_token):
        _request_token.return_value = {'access_token': 'new_access_token', 'expires_in': 10}
        self.manager._token = Token('access_token', expires_in=100)

        self.manager._update_token()

        _request_token.assert_called_once()

        self.assertEqual(self.manager._token.access_token, 'new_access_token')
        self.assertEqual(self.manager._token._expires_in, 10)

    def test_should_return_token_value(self):
        self.manager._token = Token('access_token', expires_in=10)
        self.assertEqual(self.manager.get_token(), 'access_token')

    @patch('alf.managers.TokenManager._update_token')
    @patch('alf.managers.TokenManager._has_token')
    def test_get_token_should_request_a_new_token_if_do_not_have_a_token(self, _has_token, _update_token):
        _has_token.return_value = False

        self.manager.get_token()

        _update_token.assert_called_once()
