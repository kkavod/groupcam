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

    def wait_until(self, condition, timeout):
        timeout = timeout and self.get_async_test_timeout()

#          timeout = self.io_loop.add_timeout(self.io_loop.time() + timeout, timeout_func)
#          while True:
#              self.__running = True
#              self.io_loop.start()
#              if (self.__failure is not None or
#                      condition is None or condition()):
#                  break
#          if self.__timeout is not None:
#              self.io_loop.remove_timeout(self.__timeout)


class BaseAPITestCase(BaseTestCase):
    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def get(self, path):
        return self.fetch(path)

    def post(self, path, data):
        response = self.fetch(path, method='POST', data=data)
        return response

    def put(self, path, data):
        response = self.fetch(path, method='PUT', data=data)
        return response

    def delete(self, path):
        return self.fetch(path, method='DELETE')

    def fetch(self, path, method='GET', data=None):
        """Requests data from the HTTP server using the path specified.
        """
        kwargs = dict(method=method, headers=self._headers)
        if data is not None:
            kwargs['body'] = json_encode(data)
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
