from groupcam.db import db
from groupcam.api.tests.base import BaseAPITestCase
from groupcam.api.tests.factories import CameraFactory


class TestPresets(BaseAPITestCase):
    @classmethod
    def setup_class(cls):
        cls._cameras = [CameraFactory() for index in range(7)]
        db.sync.cameras.insert(cls._cameras)

    def test_get_presets(self):
        camera_id = self._cameras[0]['id']
        camera = db.sync.cameras.find_one({'id': camera_id})

        url = self.application.reverse_url('presets', camera_id)
        resp = self.get(url)
        assert resp.code == 200
        assert len(resp.json['presets'] > 0)
        assert resp.json['presets'] == camera['presets']
