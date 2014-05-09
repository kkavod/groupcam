import operator

import motor
import colander

import tornado.web
import tornado.gen

from groupcam.db import db
from groupcam.client import manager
from groupcam.api.schemas import Preset


class BaseHandler(tornado.web.RequestHandler):
    def _filter_keys(self, instance, allowed_keys):
        """
        """

        if isinstance(instance, dict):
            result = {
                key: instance.get(key)
                for key in allowed_keys
            }
        elif isinstance(instance, list):
            result = [
                self._filter_keys(item, allowed_keys)
                for item in instance
            ]
        else:
            result = instance
        return result


class CamerasHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        cursor = db.async.cameras.find(length=255)
        cameras = yield motor.Op(cursor.to_list)
        keys = ['id', 'title', 'nickname', 'frame_url']
        result = dict(cameras=self._filter_keys(cameras, keys), ok=True)
        self.finish(result)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        camera = tornado.escape.json_decode(self.request.body)
        manager.add(camera)
        self.set_status(201)
        self.finish({'ok': True})


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
        preset = tornado.escape.json_decode(self.request.body)
        result = {}
        try:
            clean_preset = Preset().deserialize(preset)
        except colander.Invalid as e:
            self.set_status(400)
            result = dict(errors=e.asdict(), ok=False)
        else:
            upd_args = {'id': camera_id}, {'$push': {'presets': clean_preset}}
            yield motor.Op(db.async.cameras.update, *upd_args)
            self.set_status(201)
            result = {'ok': True}
        self.finish(result)


class PresetHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def update(self, camera_id, number):
        preset = tornado.escape.json_decode(self.request.body)
        result = {}
        try:
            clean_preset = Preset().deserialize(preset)
        except colander.Invalid as e:
            self.set_status(400)
            result = dict(errors=e.asdict(), ok=False)
        else:
            result = {'ok': True}
        self.finish(result)
