"""Tornado-specific py.test fixtures.
"""

import pytest

from tornado.testing import bind_unused_port
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from groupcam.api.tests.base import TestApplication
from groupcam.core import initialize


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
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
