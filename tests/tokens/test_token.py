# -*- coding: utf-8 -*-
import redis
import memcache
import unittest

from alf.managers import Token
from alf.tokens import TokenStorage, TokenDefaultStorage
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestToken(unittest.TestCase):

    def setUp(self):
        self.storage_obj = None

    @freeze_time("2015-01-01 10:00:00.117153")
    def test_expires_on_works(self):
        expires = Token.calc_expires_on(10)
        self.assertEqual(datetime.now() + timedelta(seconds=10), expires)

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
        token_storage = TokenStorage(self.storage_obj, 'test')
        token_storage(token)
        self.assertEqual(self.storage_obj.get(token_storage.token_key), 'access_token')

        expires = str(token.expires_on)
        self.assertEqual(self.storage_obj.get(token_storage.expires_key), expires, self.storage_obj)

        self.assertEqual('test_access_token', token_storage.token_key)
        self.assertEqual('test_expires_on', token_storage.expires_key)

    @freeze_time('2015-01-01 10:12:10.000000')
    def test_storage_should_respect_datetime_format(self):
        token = Token(access_token='access_token',
                      expires_on=Token.calc_expires_on(10))
        token_storage = TokenStorage(self.storage_obj)
        token_storage(token)

        expires = token_storage.request_token()['expires_on']
        expected = datetime(2015, 1, 1, 10, 12, 20, microsecond=0)
        self.assertEqual(expires, expected)

    def test_storage_should_add_retrieve_token(self):
        token = Token(access_token='access_token',
                      expires_on=Token.calc_expires_on(10))
        expires = str(token.expires_on)
        token_storage = TokenStorage(self.storage_obj)
        token_storage(token)
        token_requested = token_storage.request_token()
        self.assertEqual(len(token_requested), 2)
        self.assertEqual(self.storage_obj.get(token_storage.token_key), 'access_token')
        self.assertEqual(self.storage_obj.get(token_storage.expires_key), expires, self.storage_obj)

    def test_storage_should_add_just_once_same_value(self):
        expires_datetime = Token.calc_expires_on(10)
        token = Token(access_token='access_token',
                      expires_on=expires_datetime)
        token2 = Token(access_token='new_access_token',
                       expires_on=expires_datetime)
        expires = token.expires_on
        token_storage = TokenStorage(self.storage_obj)
        token_storage(token)
        token_storage._access_token = 'new_access_token'
        token_storage(token2)
        token_requested = token_storage.request_token()
        self.assertEqual(len(token_requested), 2)
        self.assertEqual(token_requested.get('access_token'), 'access_token')
        self.assertEqual(token_requested.get('expires_on'), expires, self.storage_obj)


class TestTokenRedis(TestTokenStorage):

    def setUp(self):
        self.storage_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        try:
            self.storage_obj.scan()
        except redis.ConnectionError:
            self.skipTest("You don't have a Redis server")

    def tearDown(self):
        self.storage_obj.flushall()


class TestTokenMemcached(TestTokenStorage):

    def setUp(self):
        self.storage_obj = memcache.Client(['127.0.0.1:11211'], debug=1)
        if not self.storage_obj.get_stats():
            self.skipTest("You don't have a Memcached server")

    def tearDown(self):
        self.storage_obj.flush_all()
