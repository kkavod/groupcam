"""Tornado-specific py.test fixtures.
"""

from time import sleep

from groupcam.db import db
from groupcam.core import initialize
from groupcam.client import manager


def pytest_runtestloop(session):
    initialize(testing=True)
    drop_collections()
    manager.run_async()
    # TODO: replace with join channel waiter
    sleep(1.)


def drop_collections():
    collections = db.sync.collection_names()
    [db.sync[collection].drop()
     for collection in collections
     if collection != 'system.indexes']
