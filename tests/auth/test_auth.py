# -*- coding: utf-8 -*-

from mock import Mock
from unittest import TestCase

from alf.auth import BearerTokenAuth


class TestBearerTokenAuth(TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.headers = {}
        self.auth = BearerTokenAuth('token')

    def test_should_add_authorization_header_to_request(self):
        self.auth(self.request)
        self.assertEqual(self.request.headers['Authorization'], 'Bearer token')

    def test_should_return_the_request_object(self):
        modified_request = self.auth(self.request)
        self.assertEqual(self.request, modified_request)
