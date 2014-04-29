import pytest

from groupcam.db import db
from groupcam.client import manager
from groupcam.api.tests.base import BaseAPITestCase
from groupcam.api.tests.factories import CameraFactory


class TestCameras(BaseAPITestCase):
    @pytest.mark.xfail
    def test_get_cameras(self):
        resp = self.get('/cameras')
        db.sync.collection.insert({'key': 2})
        assert resp.code == 200
        assert resp.json['cameras'] == {}

    @pytest.mark.xfail
    def test_post_camera(self):
        orig_clients_num = len(manager.dest_clients)
        url = self.application.reverse_url('cameras')
        camera = CameraFactory()
        response = self.post(url, camera)
        assert response.code == 201
        assert response.json['ok'] is True
        found = db.sync.cameras.find_one(camera)
        assert found is not None
        assert found['device'].startswith('/dev/video')
        assert len(manager.dest_clients) == orig_clients_num + 1
        nicknames = [str(user.nickname, 'utf8')
                     for user in manager.src_client.users]
        assert camera['nickname'] in nicknames

    @pytest.mark.xfail
    def test_post_invalid_camera(self):
        assert False
