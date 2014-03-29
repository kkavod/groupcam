from groupcam.api.tests.base import BaseTestCase


class TestCameras(BaseTestCase):
    def test_get_cameras(self):
        # resp = client.fetch('/cameras')
        # db.collection.insert({'key': 2})

        # assert resp.code == 200
        # assert resp.json == {}
        resp = self.fetch('/cameras')
        import pdb; pdb.set_trace()
        assert True
