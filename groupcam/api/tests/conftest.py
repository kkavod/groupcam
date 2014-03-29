"""Tornado-specific py.test fixtures.
"""

import json

import pytest

from tornado.testing import bind_unused_port
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPClient
from tornado.util import raise_exc_info

from groupcam.api.tests.base import TestApplication
from groupcam.core import initialize


class _TimeoutException(Exception):
    pass


class TestingClient(object):
    """A port of parts of AsyncTestCase. See tornado.testing.py:275
    """

    def __init__(self, http_server, http_client):
        self._stopped = False
        self._running = False
        self._stop_args = None
        self._failure = None
        self.http_server = http_server
        self.http_client = http_client

    @property
    def io_loop(self):
        return IOLoop.instance()

    def fetch(self, path, **kwargs):
        """This seems a bit fragile. How else to get the dynamic port number?
        """
        _, sock = self.http_server._sockets.popitem()
        _, port = sock.getsockname()
        url = 'http://localhost:{}{}'.format(port, path)
        self.http_client.fetch(url, self.stop, **kwargs)
        response = self.wait()
        if 'application/json' in response.headers['Content-Type']:
            response.json = json.loads(str(response.body, 'utf8'))
        return response

    def wait(self, condition=None, timeout=5):
        if not self._stopped:
            self._add_timeout(timeout)
            self._do_wait(condition)
            self._remove_timeout()
        assert self._stopped
        self._stopped = False
        self._rethrow()
        result = self._stop_args
        self._stop_args = None
        return result

    def stop(self, _arg=None, **kwargs):
        """Stops the IO loop.
        """
        assert _arg is None or not kwargs
        self._stop_args = kwargs or _arg
        if self._running:
            self.io_loop.stop()
            self._running = False
        self._stopped = True

    def _add_timeout(self, timeout):
        def _timeout_func():
            message = "Operation timed out after {} seconds".format(timeout)
            try:
                raise _TimeoutException(message)
            except _TimeoutException as e:
                self._failure = e.__traceback__
            self.stop()
        timestamp = self.io_loop.time() + timeout
        self._timeout = self.io_loop.add_timeout(timestamp, _timeout_func)

    def _do_wait(self, condition):
        while True:
            self._running = True
            self.io_loop.start()
            break_condition = (
                self._failure is not None or
                condition is None or
                condition()
            )
            if break_condition:
                break

    def _remove_timeout(self):
        if self._timeout is not None:
            self.io_loop.remove_timeout(self._timeout)
            self._timeout = None

    def _rethrow(self):
        if self._failure is not None:
            failure = self._failure
            self._failure = None
            raise_exc_info(failure)


@pytest.fixture(scope='module')
def client(request, app, http_server):
    """Testing client instance.
    """
    result = TestingClient(http_server, AsyncHTTPClient())
    return result


@pytest.fixture(scope='session')
def application(request):
    return TestApplication()


@pytest.fixture(scope='session')
def http_server(request, application):
    """HTTP server instance.
    """

    initialize()
    sock, port = bind_unused_port()
    server = HTTPServer(application, io_loop=IOLoop.instance())
    server.add_sockets([sock])
    return server
