import motor

import tornado.ioloop
import tornado.web

from groupcam.core import logger
from groupcam.conf import config
from groupcam.api.urls import urls


db = motor.MotorClient().open_sync().test
application = tornado.web.Application(urls, db=db)


def run_http_server():
    application.listen(config['http']['port_base'])
    logger.info("Launching HTTP server")
    tornado.ioloop.IOLoop.instance().start()
