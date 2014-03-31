import json

from groupcam.api.tests.base import BaseTestCase
from groupcam.api.tests.factories import CameraFactory


class TestCameras(BaseTestCase):
    def setup_module(self):
        pass

    def test_get_cameras(self):
        resp = self.fetch('/cameras')
        self.db.collection.insert({'key': 2})

        assert resp.code == 200
        assert resp.json == {}

    def test_post_cameras(self):
        url = self.application.reverse_url('cameras')
        camera = CameraFactory()
        import pdb; pdb.set_trace()
        response = self.fetch(url, method='POST', body=json.dumps(camera))
        assert response.code == 201
        assert response.json['ok'] is True
        # results = [item for item in self.db.collection.find()]
