from groupcam.db import db
from groupcam.api.tests.base import BaseAPITestCase
from groupcam.api.tests.factories import CameraFactory, PresetFactory


class TestPresets(BaseAPITestCase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls._cameras = [CameraFactory() for index in range(7)]
        db.sync.cameras.insert(cls._cameras)

    def setup_method(self, meth):
        self._camera = self._cameras[0]
        self._url = self.application.reverse_url('presets', self._camera['id'])

    def test_get_presets(self):
        resp = self.get(self._url)
        assert resp.code == 200
        assert len(resp.json['presets']) > 0
        assert resp.json['presets'] == self._camera['presets']

    def test_get_no_presets(self):
        url = self.application.reverse_url('presets', 'no-existing')
        assert self.get(url).code == 204

    def test_post_presets(self):
        preset = PresetFactory()
        resp = self.post(self._url, preset)
        assert resp.code == 201
        camera = db.sync.cameras.find_one({'id': self._camera['id']})
        assert preset in camera['presets']
