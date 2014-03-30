"""Tornado-specific py.test fixtures.
"""

import pytest

from groupcam.api.tests.base import TestApplication
from groupcam.core import initialize


@pytest.fixture(scope='session')
def application(request):
    """Test application instance.
    """
    initialize()
    return TestApplication()
