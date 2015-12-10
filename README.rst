alf
===

.. image:: https://travis-ci.org/globocom/alf.svg?branch=master
    :target: https://travis-ci.org/globocom/alf

Python OAuth 2 Client
---------------------

`alf` is an OAuth 2 Client based on `requests.Session
<http://docs.python-requests.org/en/latest/user/advanced/#session-objects>`_
with seamless support for the `Client Credentials Flow
<http://tools.ietf.org/html/draft-ietf-oauth-v2-31#section-1.3.4>`_.

.. image:: /assets/alf.jpeg?raw=true

Features
--------

* Automatic token retrieving and renewing
* Token expiration control
* Automatic token storage
* Automatic retry on status 401 (UNAUTHORIZED)

Usage
-----

Initialize the client and use it as a `requests.Session
<http://docs.python-requests.org/en/latest/user/advanced/#session-objects>`_
object.

.. code-block:: python

    from alf.client import Client

    alf = Client(
        token_endpoint='http://example.com/token',
        client_id='client-id',
        client_secret='secret')

    resource_uri = 'http://example.com/resource'

    alf.put(
        resource_uri, data='{"name": "alf"}',
        headers={'Content-Type': 'application/json'})

    alf.get(resource_uri)

    alf.delete(resource_uri)

Using your custom token storage
-------------------------------

Now passing an object with get and set attributes you can store or retrieve a token.

This object can be a Redis, Memcache or your custom object.

.. code-block:: python

    from alf.client import Client
    from redis import StrictRedis

    redis = StrictRedis(host='localhost', port=6379, db=0)

    alf = Client(
        token_endpoint='http://example.com/token',
        client_id='client-id',
        client_secret='secret',
        token_storage=redis)

    resource_uri = 'http://example.com/resource'

    alf.put(
        resource_uri, data='{"name": "alf"}',
        headers={'Content-Type': 'application/json'})

    alf.get(resource_uri)

    alf.delete(resource_uri)


How does it work?
-----------------

Before the request, a token will be requested on the authentication endpoint
and a JSON response with the ``access_token`` and ``expires_in`` keys will be
expected.

Multiple attempts will be issued after an error response from the endpoint if
the ``token_retries`` argument is used. Check `token-retrying`_ for more info.

``alf`` keeps the token until it is expired according to the ``expires_in``
value.

The token will be used on a `Bearer authorization
header <http://tools.ietf.org/html/draft-ietf-oauth-v2-31#section-7.1>`_ for
the original request.

.. code-block::

    GET /resource/1 HTTP/1.1
    Host: example.com
    Authorization: Bearer token-12312

If the request fails with a 401 (UNAUTHORIZED) status, a new token is retrieved
from the endpoint and the request is retried. This happens only once, if it
fails again the error response is returned.

The token will be reused for every following request until it is expired.


.. _token-retrying:

Token Retrying
--------------

The client supports the `retry interface from urllib3 <https://urllib3.readthedocs.org/en/latest/helpers.html?highlight=retry#module-urllib3.util.retry>`_ to repeat attempts to
retrieve the token from the endpoint.

The following code will retry the token request 5 times when the response status
is 500 and it will wait 0.3 seconds longer after each error (known as
`backoff <https://en.wikipedia.org/wiki/Exponential_backoff>`_).

.. code-block:: python

    from requests.packages.urllib3.util import Retry
    from alf.client import Client

    alf = Client(
        token_endpoint='http://example.com/token',
        client_id='client-id',
        client_secret='secret',
        token_retry=Retry(total=5, status_forcelist=[500], backoff_factor=0.3))

Workflow
--------

.. image:: /assets/workflow.png?raw=true

Troubleshooting
---------------

In case of an error retrieving a token, the error response will be returned,
the real request won't happen.


Related projects
----------------

`djalf <https://github.com/viniciuschagas/djalf>`_
''''''''''''''''''''''''''''''''''''''''''''''''''

An extended client that uses Django's cache backend to share tokens between
server instances.


`tornado-alf <https://github.com/globocom/tornado-alf>`_
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

A port of the `alf` client using tornado's `AsyncHTTPClient`.
