from groupcam.db import db
from groupcam.api.tests.base import BaseAPITestCase
from groupcam.api.tests.factories import CameraFactory, PresetFactory


class TestPresets(BaseAPITestCase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls._cameras = [CameraFactory() for index in range(7)]
        db.sync.cameras.insert(cls._cameras)
        cls._camera = cls._cameras[0]
        cls._url = cls.application.reverse_url('presets', cls._camera['id'])

    def test_get_presets(self):
        resp = self.get(self._url)
        assert resp.code == 200
        assert len(resp.json['presets']) > 0
        assert resp.json['presets'] == self._camera['presets']

    def test_get_no_presets(self):
        url = self.application.reverse_url('presets', 'no-existing')
        assert self.get(url).code == 204

    def test_post_preset(self):
        preset = PresetFactory()
        resp = self.post(self._url, preset)
        assert resp.code == 201
        assert resp.json['number'] == len(self._camera['presets']) + 1
        camera = self.get_camera(self._camera['id'])
        assert preset in camera['presets']

    def test_post_invalid_preset(self):
        invalid_preset = dict(PresetFactory(), name=None)
        resp = self.post(self._url, invalid_preset)
        assert resp.code == 400
        assert list(resp.json['errors']) == ['name']


class TestPreset(BaseAPITestCase):
    def setup_method(self, meth):
        self._camera = CameraFactory()
        db.sync.cameras.insert(self._camera)
        self._preset = self._camera['presets'][0]
        self._url = self.application.reverse_url(
            'preset', self._camera['id'], 1)

    def test_update_preset(self):
        preset = PresetFactory()
        resp = self.put(self._url, preset)
        assert resp.code == 200
        camera = self.get_camera(self._camera['id'])
        assert camera['presets'][0] == preset

    def test_update_preset_improperly(self):
        invalid_preset = dict(self._preset, layout="invalid")
        resp = self.put(self._url, invalid_preset)
        assert resp.code == 400
        self._verify_camera_is_unchanged()

    def test_delete_preset(self):
        resp = self.delete(self._url)
        assert resp.code == 200
        camera = self.get_camera(self._camera['id'])
        assert camera['presets'] == self._camera['presets'][1:]

    def test_delete_invalid_preset(self):
        invalid_number = len(self._camera['presets']) + 1
        preset_url = self.application.reverse_url(
            'preset', self._camera['id'], invalid_number)
        resp = self.delete(preset_url)
        assert resp.code == 404
        assert not resp.json['ok']
        self._verify_camera_is_unchanged()

    def _verify_camera_is_unchanged(self):
        camera = self.get_camera(self._camera['id'])
        assert camera == self._camera
