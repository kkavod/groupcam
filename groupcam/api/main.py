import tornado.ioloop
import tornado.web

from groupcam.core import logger
from groupcam.conf import config
from groupcam.api.urls import urls


class Application(tornado.web.Application):
    def __init__(self):
        super().__init__(urls)


def run_http_server():
    application = Application()
    application.listen(config['http']['port_base'])
    logger.info("Launching HTTP server")
    tornado.ioloop.IOLoop.instance().start()
