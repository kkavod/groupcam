import motor

import tornado.ioloop
import tornado.web

from groupcam.core import logger
from groupcam.conf import config
from groupcam.api.urls import urls


class Application(tornado.web.Application):
    def __init__(self):
        super().__init__(urls)
        self._init_database()

    def _init_database(self):
        motor_client = motor.MotorClient(config['database']['uri']).open_sync()
        self.db = motor_client[config['database']['name']]


def run_http_server():
    application = Application()
    application.listen(config['http']['port_base'])
    logger.info("Launching HTTP server")
    tornado.ioloop.IOLoop.instance().start()
