import tornado.ioloop
from tornado.testing import AsyncHTTPTestCase
from tornado.escape import json_decode, json_encode

from groupcam.api.main import Application


class TestApplication(Application):
    def __init__(self):
        super().__init__()


class BaseTestCase(AsyncHTTPTestCase):
    @classmethod
    def setup_class(cls):
        cls.application = TestApplication()

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def get_app(self):
        return self.application


class BaseAPITestCase(BaseTestCase):
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def get(self, path):
        return self.fetch(path, headers=self._headers)

    def post(self, path, data):
        response = self.fetch(path, method='POST',
                              headers=self._headers,
                              body=json_encode(data))
        return response

    def update(self, path, data):
        response = self.fetch(path, method='UPDATE',
                              headers=self._headers,
                              body=json_encode(data))
        return response

    def delete(self, path):
        return self.fetch(path, method='DELETE',
                          headers=self._headers)

    def fetch(self, path, **kwargs):
        """Requests data from the HTTP server using the path specified.
        """
        response = super().fetch(path, **kwargs)
        self._update_response_with_json(response)
        return response

    def _update_response_with_json(self, response):
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            body = str(response.body, 'utf8')
            response.json = json_decode(body)
        else:
            response.json = {}
