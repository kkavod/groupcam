import tornado.ioloop
import tornado.web

from groupcam.conf import conf


class CamerasHandler(tornado.web.RequestHandler):
    def post(self):
        pass


application = tornado.web.Application([
    (r'', CamerasHandler),
])


if __name__ == "__main__":
    application.listen(5000)
    tornado.ioloop.instance().start()
