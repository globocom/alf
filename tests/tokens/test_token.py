# -*- coding: utf-8 -*-
import redis
import memcache
import unittest

from alf.managers import Token
from alf.tokens import TokenStorage, TokenDefaultStorage, TOKEN_KEY, TOKEN_EXPIRES
from datetime import datetime, timedelta

class TestToken(unittest.TestCase):

    def setUp(self):
        self.storage_obj = None

    def test_expires_on_works(self):
        expires = Token.calc_expires_on(10)
        self.assertGreater(datetime.now() + timedelta(seconds=10), expires)

    def test_should_have_an_access_token(self):
        token = Token(access_token='access_token')
        self.assertEqual(token.access_token, 'access_token')

    def test_should_know_when_it_has_expired(self):
        token = Token(access_token='access_token',
                      expires_on=0)
        self.assertFalse(token.is_valid(), self.storage_obj)

    def test_should_know_when_it_is_valid(self):
        token = Token(access_token='access_token',
                      expires_on=Token.calc_expires_on(10))
        self.assertTrue(token.is_valid(), self.storage_obj)


class TestTokenStorage(unittest.TestCase):

    def setUp(self):
        self.storage_obj = TokenDefaultStorage()

    def test_storage_should_add_token(self):
        token = Token(access_token='access_token',
                      expires_on=Token.calc_expires_on(10))
        token_storage = TokenStorage(self.storage_obj)
        token_storage(token)
        self.assertEqual(self.storage_obj.get(TOKEN_KEY), 'access_token')

        expires = str(token.expires_on)
        self.assertEqual(self.storage_obj.get(TOKEN_EXPIRES), expires, self.storage_obj)

    def test_storage_should_add_retrieve_token(self):
        token = Token(access_token='access_token',
                      expires_on=Token.calc_expires_on(10))
        expires = str(token.expires_on)
        token_storage = TokenStorage(self.storage_obj)
        token_storage(token)
        token_requested = token_storage.request_token()
        self.assertEqual(len(token_requested), 2)
        self.assertEqual(token_requested.get('access_token'), 'access_token')
        self.assertEqual(self.storage_obj.get('expires_on'), expires, self.storage_obj)


class TestTokenRedis(TestTokenStorage):

    def setUp(self):
        self.storage_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        try:
            self.storage_obj.scan()
        except redis.ConnectionError:
            self.skipTest("You don't have a Redis server")

    def tearDown(self):
        self.storage_obj.delete('access_token')


class TestTokenMemcached(TestTokenStorage):

    def setUp(self):
        self.storage_obj = memcache.Client(['127.0.0.1:11211'], debug=1)
        if not self.storage_obj.get_stats():
            self.skipTest("You don't have a Memcached server")

    def tearDown(self):
        self.storage_obj.delete('access_token')

