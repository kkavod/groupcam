"""Tornado-specific py.test fixtures.
"""

import pytest

from groupcam.core import initialize
from groupcam.api.main import Application


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize(testing=True)
    return Application()
