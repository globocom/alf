# -*- coding: utf-8 -*-
from mock import patch

from unittest import TestCase

from alf.managers import Token, TokenDjango


class TestTokenDjango(TestCase):

    def test_should_be_a_subclass_of_Token(self):
        self.assertTrue(issubclass(TokenDjango, Token))

    def test_access_token_property(self):
        token = Token(access_token='access_token')
        self.assertEqual(token.access_token, 'access_token')

    def test_should_know_when_it_has_expired(self):
        token = Token(access_token='access_token', expires_in=0)
        self.assertFalse(token.is_valid())

    def test_should_know_when_it_is_valid(self):
        token = Token(access_token='access_token', expires_in=10)
        self.assertTrue(token.is_valid())

    def test_access_token_setter_should_update_the_access_token(self):
        token = Token()
        token.access_token = 'new-access-token'

        self.assertEquals(token._access_token, 'new-access-token')

    @patch('alf.tokens.Token._update_expires_on')
    def test_expires_in_setter_should_update_the_expires_in_and_call_update_expires_on(self, _update_expires_on):
        token = Token()
        token.expires_in = 10

        _update_expires_on.assert_called_with()
        self.assertEquals(_update_expires_on.call_count, 2)

        self.assertEquals(token._expires_in, 10)

    @patch('alf.tokens.datetime')
    @patch('alf.tokens.timedelta')
    def test_update_expires_on_should_update_expires_on_value(self, timedelta, datetime):
        token = Token()
        token._expires_in = 10

        datetime.now.return_value = 10
        timedelta.return_value = 10

        token._update_expires_on()

        timedelta.assert_called_with(seconds=10)
        self.assertEquals(timedelta.call_count, 2)

        self.assertEquals(token._expires_on, 20)
