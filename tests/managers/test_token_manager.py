# -*- coding: utf-8 -*-

from unittest import TestCase

from alf.managers import TokenManager, Token, TokenError
from freezegun import freeze_time
from mock import Mock, patch


class BaseTokenManagerTestCase(TestCase):
    END_POINT = 'http://endpoint/token'
    CLIENT_ID = 'client_id'
    CLIENT_SECRET = 'client_secret'


class TokenManagerTestCase(BaseTokenManagerTestCase):

    def setUp(self):
        with patch('alf.managers.mount_retry_adapter') as self.mount_adapter:
            self.manager = TokenManager(
                self.END_POINT, self.CLIENT_ID, self.CLIENT_SECRET)

    def test_should_start_with_no_token(self):
        self.assertFalse(self.manager._has_token())

    def test_should_define_right_base_key_to_token_storage(self):
        self.assertEqual(
            '{}_{}'.format(self.END_POINT, self.CLIENT_ID),
            self.manager._token_storage._base_key
        )

    def test_should_NOT_setup_token_retries_by_default(self):
        self.assertEqual(self.mount_adapter.call_count, 0)

    def test_should_detect_expired_token(self):
        self.manager._token = Token('', expires_on=Token.calc_expires_on(0))
        self.assertFalse(self.manager._has_token())

    def test_should_respect_valid_token(self):
        self.manager._token = Token('', expires_on=Token.calc_expires_on(10))
        self.assertTrue(self.manager._has_token())

    @freeze_time("2015-01-01 10:00:00.117153")
    def test_should_reset_token(self):
        self.manager.reset_token()

        self.assertEqual(self.manager._token.access_token, '')
        self.assertEqual(self.manager._token.expires_on,
                         Token.calc_expires_on(0))

    @patch('requests.Session.post')
    def test_should_be_able_to_request_a_new_token(self, post):
        post.return_value.json.return_value = {
            'access_token': 'accesstoken',
            'expires_on': Token.calc_expires_on(10),
        }

        self.manager._request_token()

        post.assert_called_with(self.END_POINT,
                                timeout=None,
                                data={'grant_type': 'client_credentials'},
                                auth=(self.CLIENT_ID, self.CLIENT_SECRET))

    @patch('requests.Session.post')
    def test_should_have_token_request_timeout(self, post):
        post.return_value.json.return_value = {}
        manager = TokenManager(
            self.END_POINT, self.CLIENT_ID, self.CLIENT_SECRET,
            token_request_params={
                'timeout': 5
            }
        )

        manager._request_token()

        post.assert_called_with(self.END_POINT,
                                timeout=5,
                                data={'grant_type': 'client_credentials'},
                                auth=(self.CLIENT_ID, self.CLIENT_SECRET))

    @patch('requests.Session.post')
    def test_should_raise_token_error_for_bad_token(self, post):
        post.return_value = Mock()
        post.return_value.ok = False
        post.return_value.status_code = 500

        with self.assertRaises(TokenError) as context:
            self.manager._request_token()

        self.assertEqual(context.exception.response.status_code, 500)

    @patch('alf.managers.TokenManager._request_token')
    def test_get_token_data_should_obtain_new_token(self, _request_token):
        self.manager.reset_token()

        self.manager._get_token_data()

        self.assertTrue(_request_token.called)

    @patch('alf.managers.TokenManager._request_token')
    @freeze_time("2015-01-01 10:00:00.117153")
    def test_update_token_should_set_a_token_with_data_retrieved(self, _request_token):
        self.manager.reset_token()
        expires = 100
        _request_token.return_value = {'access_token': 'new_access_token',
                                       'expires_in': expires}

        self.manager._token = Token('access_token',
                                    expires_on=0)

        self.manager._update_token()

        self.assertTrue(_request_token.called)

        self.assertEqual(self.manager._token.access_token, 'new_access_token')
        self.assertEqual(self.manager._token.expires_on, Token.calc_expires_on(expires))

    @patch('alf.managers.TokenManager._request_token')
    def test_update_token_should_set_a_token_with_data_retrieved_from_storage(self, _request_token):
        expires = Token.calc_expires_on(100)
        _request_token.return_value = dict()

        self.manager._token = Token('new_access_token',
                                    expires_on=expires)

        self.manager._token_storage(self.manager._token)

        self.manager._update_token()

        self.assertFalse(_request_token.called)

        self.assertEqual(self.manager._token.access_token, 'new_access_token')
        self.assertEqual(self.manager._token.expires_on, expires)

    def test_should_return_token_value(self):
        self.manager._token = Token('access_token', expires_on=Token.calc_expires_on(10))
        self.assertEqual(self.manager.get_token(), 'access_token')

    @patch('alf.managers.TokenManager._update_token')
    @patch('alf.managers.TokenManager._has_token')
    def test_get_token_should_request_a_new_token_if_do_not_have_a_token(self, _has_token, _update_token):
        _has_token.return_value = False

        self.manager.get_token()

        self.assertTrue(_update_token.called)


class TokenManagerWithRetriesTestCase(BaseTokenManagerTestCase):

    def test_should_start_with_no_token(self):
        with patch('alf.managers.mount_retry_adapter') as self.mount_adapter:
            self.manager = TokenManager(
                self.END_POINT, self.CLIENT_ID, self.CLIENT_SECRET,
                token_retries=44)

        self.mount_adapter.assert_called_once_with(
            self.manager._session, 44)
