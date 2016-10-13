# -*- coding: utf-8 -*-

from mock import patch, Mock
from unittest import TestCase

from alf.managers import TokenManager
from alf.client import Client, BearerTokenAuth


class TestClient(TestCase):

    end_point = 'http://endpoint/token'
    resource_url = 'http://api/some/resource'

    def test_Client_should_have_a_variable_with_a_token_manager_class(self):
        self.assertEquals(Client.token_manager_class, TokenManager)

    def test_token_manager_object_should_be_an_instance_of_token_manager_class(self):
        client = Client(token_endpoint=self.end_point, client_id='client-id', client_secret='client_secret')

        self.assertTrue(isinstance(client._token_manager, client.token_manager_class))

    @patch('alf.client.TokenManager.__init__')
    def test_should_have_token_request_timeout(self, init):
        init.return_value = None

        client = Client(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret',
            token_request_params={
                'timeout': 10
            }
        )

        init.assert_called_with(client_id='client_id',
                                client_secret='client_secret',
                                token_endpoint=self.end_point,
                                token_request_params={
                                    'timeout': 10
                                },
                                token_retries=None,
                                token_storage=None)

    @patch('alf.client.TokenManager')
    @patch('requests.Session.request')
    def test_should_retry_a_bad_request_once(self, request, Manager):
        request.return_value = Mock(status_code=401)
        self._fake_manager(Manager, has_token=False)

        self._request(Manager)

        self.assertEqual(request.call_count, 2)

    @patch('requests.Session.post')
    @patch('requests.Session.request')
    def test_should_stop_the_request_when_token_fails(self, request, post):
        post.return_value = Mock(status_code=500, ok=False)

        client = Client(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret'
        )

        response = client.request('GET', self.resource_url)

        self.assertEqual(response.status_code, 500)

    @patch('alf.client.TokenManager.reset_token')
    @patch('requests.Session.post')
    @patch('requests.Session.request')
    def test_should_reset_token_when_token_fails(self, request, post, reset_token):
        post.return_value = Mock(status_code=500, ok=False)

        client = Client(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret'
        )

        response = client.request('GET', self.resource_url)

        self.assertTrue(reset_token.called)

        self.assertEqual(response.status_code, 500)

    @patch('alf.client.TokenManager._has_token')
    @patch('alf.client.TokenManager.reset_token')
    @patch('requests.Session.request')
    def test_should_reset_token_when_gets_an_unauthorized_error(self, request, reset_token, _has_token):
        request.return_value = Mock(status_code=401)
        _has_token.return_value = True

        client = Client(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret'
        )

        response = client.request('GET', self.resource_url)

        self.assertTrue(reset_token.called)

        self.assertEqual(response.status_code, 401)

    @patch('requests.Session.request')
    def assertRequestsResource(self, Manager, access_token, status_code, request):
        request.return_value = Mock(status_code=status_code)
        self._request(Manager)

        self.assertTrue(request.called)
        self.assertResourceWasRequested(request.call_args, access_token=access_token)

    def assertResourceWasRequested(self, call, access_token):
        args, kwargs = call
        self.assertEqual(args, ('GET', self.resource_url))

        auth = kwargs['auth']
        self.assertIsInstance(auth, BearerTokenAuth)
        self.assertEqual(auth._access_token, access_token)

    def _request(self, manager):
        class ClientTest(Client):
            token_manager_class = manager

        client = ClientTest(
            token_endpoint=self.end_point,
            client_id='client_id',
            client_secret='client_secret')

        return client.request('GET', self.resource_url)

    def _fake_manager(self, Manager, has_token=True, access_token='', status_code=200):
        if not isinstance(access_token, list):
            access_token = [access_token]

        access_token.reverse()

        manager = Mock()
        manager._has_token.return_value = has_token
        manager.get_token.return_value = access_token[0]
        manager.request_token.return_value = Mock(
            status_code=status_code, ok=(status_code == 200))
        Manager.return_value = manager

        return manager
