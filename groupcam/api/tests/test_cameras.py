from groupcam.db import db
from groupcam.api.tests.base import BaseJSONTestCase
from groupcam.api.tests.factories import CameraFactory


class TestCameras(BaseJSONTestCase):
    def test_get_cameras(self):
        resp = self.get('/cameras')
        db.sync.collection.insert({'key': 2})
        assert resp.code == 200
        assert resp.json == {}

    def test_post_cameras(self):
        url = self.application.reverse_url('cameras')
        camera = CameraFactory()
        response = self.post(url, camera)
        assert response.code == 201
        assert response.json['ok'] is True
        found = db.sync.cameras.find_one(camera)
        assert found is not None
        assert found['device'].startswith('/dev/video')
