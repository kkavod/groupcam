import motor

import tornado.ioloop
import tornado.web

from groupcam.core import logger
from groupcam.conf import config
from groupcam.api.urls import urls


def run_http_server():
    nosql = motor.MotorClient(config['database']['uri']).open_sync()
    db = nosql[config['database']['name']]
    application = tornado.web.Application(urls, nosql=nosql, db=db)

    application.listen(config['http']['port_base'])
    logger.info("Launching HTTP server")
    tornado.ioloop.IOLoop.instance().start()
