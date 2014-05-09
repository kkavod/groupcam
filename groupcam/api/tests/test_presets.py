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
        camera = db.sync.cameras.find_one({'id': self._camera['id']})
        assert preset in camera['presets']

    def test_post_invalid_preset(self):
        invalid_preset = dict(PresetFactory(), name=None)
        resp = self.post(self._url, invalid_preset)
        assert resp.code == 400
        assert list(resp.json['errors']) == ['name']


class TestPreset(BaseAPITestCase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls._camera = CameraFactory()
        db.sync.cameras.insert(cls._camera)
        cls._preset = cls._camera['presets'][0]
        cls._url = cls.application.reverse_url(
            'preset', cls._camera['id'], cls._preset['number'])

    def test_update_preset(self):
        pass

    def test_update_preset_improperly(self):
        invalid_preset = dict(self._preset, number="invalid")
        resp = self.put(self._url, invalid_preset)
        assert resp.code == 400
