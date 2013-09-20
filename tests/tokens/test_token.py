# -*- coding: utf-8 -*-
from unittest import TestCase

from alf.managers import Token


class TestToken(TestCase):

    def test_should_have_an_access_token(self):
        token = Token(access_token='access_token')
        self.assertEqual(token._access_token, 'access_token')

    def test_access_token_property(self):
        token = Token(access_token='access_token')
        self.assertEqual(token.access_token, 'access_token')

    def test_should_know_when_it_has_expired(self):
        token = Token(access_token='access_token', expires_in=0)
        self.assertFalse(token.is_valid())

    def test_should_know_when_it_is_valid(self):
        token = Token(access_token='access_token', expires_in=10)
        self.assertTrue(token.is_valid())
