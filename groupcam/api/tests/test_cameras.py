from groupcam.api.tests.base import BaseTestCase


class TestCameras(BaseTestCase):
    def test_get_cameras(self):
        resp = self.fetch('/cameras')
        self.db.collection.insert({'key': 2})
        results = [item for item in self.db.collection.find()]

        assert resp.code == 200
        assert resp.json == {}
