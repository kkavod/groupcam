"""Tornado-specific py.test fixtures.
"""

import pytest

from groupcam.conf import config
from groupcam.core import initialize
from groupcam.client import manager
from groupcam.tt4.client import BaseClient
from groupcam.api.main import Application


class TestApplication(Application):
    def __init__(self):
        super().__init__()
        self.tt4_client = BaseClient(config['server']['source'])


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize(testing=True)
    manager.run_async()
    return Application()
