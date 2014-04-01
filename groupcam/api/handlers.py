import motor

import tornado.escape
import tornado.web
import tornado.gen


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db


class CamerasHandler(BaseHandler):
    def get(self):
        response = {}
        self.write(response)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        camera = tornado.escape.json_decode(self.request.body)
        yield motor.Op(self.db.cameras.insert, camera)
        self.clear()
        self.set_status(201)
        self.finish({'ok': True})
