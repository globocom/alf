# -*- coding: utf-8 -*-

from unittest import TestCase

from mock import Mock, patch

from alf.adapters import mount_retry_adapter


class MountRetryAdapterTestCase(TestCase):

    @patch('requests.adapters.HTTPAdapter')
    def test_mounts_HTTP_adapter_with_retry(self, HTTPAdapter):
        number_or_retry_object = Mock()

        adapter = Mock()
        HTTPAdapter.return_value = adapter

        session = Mock()
        mount_retry_adapter(session, retries=number_or_retry_object)

        HTTPAdapter.assert_called_once_with(max_retries=number_or_retry_object)

        session.mount.assert_any_call('http://', adapter)
        session.mount.assert_any_call('https://', adapter)
