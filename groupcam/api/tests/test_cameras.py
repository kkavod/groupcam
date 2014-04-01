import json

from groupcam.api.tests.base import BaseJSONTestCase
from groupcam.api.tests.factories import CameraFactory


class TestCameras(BaseJSONTestCase):
    def setup_module(self):
        pass

    def test_get_cameras(self):
        resp = self.get('/cameras')
        self.db.collection.insert({'key': 2})
        assert resp.code == 200
        assert resp.json == {}

    def test_post_cameras(self):
        url = self.application.reverse_url('cameras')
        camera = CameraFactory()
        response = self.post(url, camera)
        assert response.code == 201
        assert response.json['ok'] is True
        found = self.db.cameras.find_one(camera)
        assert found is not None
