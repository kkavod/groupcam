import motor

import tornado.escape
import tornado.web
import tornado.gen

from groupcam.db import db
from groupcam.client import manager


class CamerasHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        cursor = db.async.cameras.find()
        cameras = yield motor.Op(cursor.to_list)
        result = dict(cameras=cameras, ok=True)
        self.finish(result)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        camera = tornado.escape.json_decode(self.request.body)
        manager.add(camera)
        self.set_status(201)
        self.finish({'ok': True})
