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

        validated = self.validate_resource(**self.path_kwargs)
        if validated and self.request.method in ('POST', 'PUT'):
            self._validate_json()

    def validate_resource(self, **kwargs):
        """Override this method to make resource path checks before calling
        HTTP method handlers.

        @return: True if the resource is valid
        """
        return True

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

    @tornado.gen.coroutine
    def get_camera(self, camera_id):
        camera = yield motor.Op(db.async.cameras.find_one, {'id': camera_id})
        return camera

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
        camera = yield self.get_camera(camera_id)
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
        camera = yield self.get_camera(camera_id)
        number = camera['presets'].index(self.clean_data) + 1
        self.finish(dict(number=number, ok=True))


class PresetHandler(BaseHandler):
    schema = Preset

    @tornado.web.asynchronous
    @tornado.gen.engine
    def put(self, camera_id, number):
        field_name = self._get_indexed_field_name(number)
        operation = {'$set': {field_name: self.clean_data}}
        yield motor.Op(db.async.cameras.update, {'id': camera_id}, operation)
        self.finish(self.result)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def delete(self, camera_id, number):
        field_name = self._get_indexed_field_name(number)
        unset = {'$unset': {field_name: 1}}
        pull = {'$pull': {'presets': None}}
        for operation in [unset, pull]:
            yield motor.Op(db.async.cameras.update,
                           {'id': camera_id}, operation)
        self.finish(dict(ok=True))

    @tornado.gen.coroutine
    def validate_resource(self, camera_id, number):
        camera = yield self.get_camera(camera_id)
        if len(camera['presets']) >= int(number):
            validated = True
        else:
            validated = False
            self.set_status(404)
            result = dict(reason="Invalid preset number", ok=False)
            self.finish(result)
        return validated

    def _get_indexed_field_name(self, number):
        index = int(number) - 1
        return 'presets.{}'.format(index)
