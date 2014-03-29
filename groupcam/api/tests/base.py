import json

import motor
import pymongo

import pytest

from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPClient, AsyncHTTPTestCase

from groupcam.conf import config
from groupcam.api.main import Application


class TestApplication(Application):
    def _init_database(self):
        motor_client = motor.MotorClient().open_sync()
        self.db = motor_client[config['database']['testing_name']]


class BaseTestCase(AsyncHTTPTestCase):
    @pytest.fixture(autouse=True)
    def initialize(self, request, application, http_server):
        self.application = application
        self.http_server = http_server
        self.http_client = AsyncHTTPClient()
        self._init_database()
        self._drop_database()

    def fetch(self, path, **kwargs):
        """Requests data from the HTTP server using the path specified.
        """
        response = AsyncHTTPTestCase.fetch(self, path, **kwargs)
        self._alter_response_with_json(response)
        return response

    def get_app(self):
        return self.application

    def get_url(self, path):
        """Constructs URL from path.
        """
        sock = next(iter(self.http_server._sockets.values()))
        _, port = sock.getsockname()
        url = 'http://localhost:{}{}'.format(port, path)
        return url

    def _init_database(self):
        mongo_client = pymongo.MongoClient()
        self.db = mongo_client[config['database']['testing_name']]

    def _drop_database(self):
        collections = self.db.collection_names()
        [self.db[collection].drop()
         for collection in collections
         if collection != 'system.indexes']

    def _alter_response_with_json(self, response):
        if 'application/json' in response.headers['Content-Type']:
            response.json = json.loads(str(response.body, 'utf8'))
        else:
            response.json = {}
