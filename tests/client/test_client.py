# -*- coding: utf-8 -*-

from mock import patch, Mock
from unittest import TestCase

from alf.client import Client, BearerTokenAuth


class TestClient(TestCase):

    end_point = 'http://endpoint/token'
    resource_url = 'http://api/some/resource'

    @patch('alf.client.SimpleTokenManager')
    def test_should_request_a_token_when_there_is_none(self, Manager):
        manager = self._fake_manager(Manager, has_token=False, access_token='new_token')
        self.assertRequestsResource('new_token', 200)
        self.assertTrue(manager.request_token.called)

    @patch('alf.client.SimpleTokenManager')
    def test_should_not_request_a_token_when_there_is_one(self, Manager):
        manager = self._fake_manager(Manager, has_token=True)
        self.assertRequestsResource('', 200)
        self.assertFalse(manager.request_token.called)

    @patch('alf.client.SimpleTokenManager')
    @patch('requests.Session.request')
    def test_should_refresh_token_when_the_request_fails(self, request, Manager):
        request.return_value = Mock(status_code=401)
        self._fake_manager(
            Manager, has_token=True, access_token=['old', 'new'])

        self._request()

        self.assertResourceWasRequested(
            request.call_args_list[0], access_token='old')
        self.assertResourceWasRequested(
            request.call_args_list[1], access_token='new')

    @patch('requests.post')
    @patch('requests.Session.request')
    def test_should_stop_the_request_when_token_fails(self, request, post):
        post.return_value = Mock(status_code=500, ok=False)
        response = self._request()

        self.assertFalse(request.called)
        self.assertEqual(response.status_code, 500)

    @patch('requests.Session.request')
    def assertRequestsResource(self, access_token, status_code, request):
        request.return_value = Mock(status_code=status_code)
        self._request()

        self.assertTrue(request.called)
        self.assertResourceWasRequested(request.call_args, access_token=access_token)

    def assertResourceWasRequested(self, call, access_token):
        args, kwargs = call
        self.assertEqual(args, ('GET', self.resource_url))

        auth = kwargs['auth']
        self.assertIsInstance(auth, BearerTokenAuth)
        self.assertEqual(auth._access_token, access_token)

    def _request(self):
        client = Client(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret')
        return client.request('GET', self.resource_url)

    def _fake_manager(self, Manager, has_token=True, access_token='', status_code=200):
        if not isinstance(access_token, list):
            access_token = [access_token]

        access_token.reverse()

        manager = Mock()
        manager.has_token.return_value = has_token
        manager.get_token = access_token.pop
        manager.request_token.return_value = Mock(
            status_code=status_code, ok=(status_code == 200))
        Manager.return_value = manager

        return manager
