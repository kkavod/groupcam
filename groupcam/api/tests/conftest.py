"""Tornado-specific py.test fixtures.
"""

import pytest

from groupcam.conf import config
from groupcam.core import initialize
from groupcam.client import manager
from groupcam.tt4.client import BaseClient
from groupcam.api.main import Application


class TestClient(BaseClient):
    def __init__(self):
        server_config = dict(
            config['server']['source'],
            nickname="Groupcam Test"
        )
        super().__init__(server_config)

        self._users = {}

    def on_command_user_joined(self, message):
        user = self._tt4.get_user(message.first_param)
        self._users[message.first_param] = user

    def on_command_user_left(self, message):
        del self._users[message.first_param]


class TestApplication(Application):
    def __init__(self):
        super().__init__()
        self.tt4_client = TestClient()


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize(testing=True)
    manager.run_async()
    return Application()
