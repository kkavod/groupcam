import operator

import motor
import colander

import tornado.web
import tornado.gen

from groupcam.db import db
from groupcam.client import manager
from groupcam.api.schemas import Camera, Preset


class BaseHandler(tornado.web.RequestHandler):
    schema = None

    def prepare(self):
        """Runs data validation on POST and PUT.
        """

        if self.request.method in ('POST', 'PUT'):
            self._validate_json()

    def filter_keys(self, obj, allowed_keys):
        """Removes all the unnecessary keys from the given object.

        @param obj: a dict or a list of dicts
        @param allowed_keys: keys to preserve
        @return: filtered object
        """

        if isinstance(obj, dict):
            result = {key: obj.get(key)
                      for key in allowed_keys}
        elif isinstance(obj, list):
            result = [self.filter_keys(item, allowed_keys)
                      for item in obj]
        else:
            result = obj
        return result

    def _validate_json(self):
        """Validates JSON body within the given Colander schema.
        """

        data = tornado.escape.json_decode(self.request.body)
        try:
            self.clean_data = self.schema().deserialize(data)
        except colander.Invalid as e:
            self.set_status(400)
            self.result = dict(errors=e.asdict(), ok=False)
            self.finish(self.result)
        else:
            status = 201 if self.request.method == 'POST' else 200
            self.set_status(status)
            self.result = {'ok': True}


class CamerasHandler(BaseHandler):
    schema = Camera

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        cursor = db.async.cameras.find(length=255)
        cameras = yield motor.Op(cursor.to_list)
        keys = ['id', 'title', 'nickname', 'frame_url']
        result = dict(cameras=self.filter_keys(cameras, keys), ok=True)
        self.finish(result)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        yield manager.add(self.clean_data)
        self.finish(self.result)


class UsersHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        users = (dict(id=user_id, name=str(user.nickname, 'utf8'))
                 for user_id, user in manager.src_client.users.items())
        sorted_users = sorted(users, key=operator.itemgetter('name'))
        if sorted_users:
            result = dict(users=sorted_users, ok=True)
        else:
            result = None
            self.set_status(204)
        self.finish(result)


class PresetsHandler(BaseHandler):
    schema = Preset

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, camera_id):
        camera = yield motor.Op(db.async.cameras.find_one, {'id': camera_id})
        if camera is None:
            result = None
            self.set_status(204)
        else:
            result = dict(presets=camera.get('presets', []), ok=True)
        self.finish(result)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, camera_id):
        upd_args = {'id': camera_id}, {'$push': {'presets': self.clean_data}}
        yield motor.Op(db.async.cameras.update, *upd_args)
        self.finish(self.result)


class PresetHandler(BaseHandler):
    schema = Preset

    @tornado.web.asynchronous
    @tornado.gen.engine
    def put(self, camera_id, number):
        self.finish(self.result)
