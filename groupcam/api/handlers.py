import tornado.web


class CamerasHandler(tornado.web.RequestHandler):
    def get(self):
        response = {}
        self.write(response)

    def post(self):
        pass
