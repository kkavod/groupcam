"""Tornado-specific py.test fixtures.
"""

import pytest

from groupcam.core import initialize
from groupcam.client import manager
from groupcam.api.main import Application


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize(testing=True)
    manager.run_async()
    return Application()
