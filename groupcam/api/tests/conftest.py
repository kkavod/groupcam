"""Tornado-specific py.test fixtures.
"""

from time import sleep

import pytest

from groupcam.core import initialize
from groupcam.client import manager
from groupcam.api.main import Application


class TestApplication(Application):
    def __init__(self):
        super().__init__()


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize(testing=True)
    manager.run_async()
    # TODO: replace with join channel waiter
    sleep(1.)
    return TestApplication()
