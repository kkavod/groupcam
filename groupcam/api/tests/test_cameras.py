import threading

import pytest

from groupcam.db import db
from groupcam.client import manager
from groupcam.api.tests.base import BaseAPITestCase
from groupcam.api.tests.factories import CameraFactory


class TestCameras(BaseAPITestCase):
    def setup_method(self, method):
        self._url = self.application.reverse_url('cameras')

    @pytest.mark.xfail
    def test_get_cameras(self):
        resp = self.get('/cameras')
        db.sync.collection.insert({'key': 2})
        assert resp.code == 200
        assert resp.json['cameras'] == {}

    def test_post_camera(self):
        orig_threads_num = threading.active_count()
        camera = CameraFactory()
        response = self.post(self._url, camera)
        assert response.code == 201
        assert response.json['ok'] is True
        del camera['presets']
        found = db.sync.cameras.find_one(camera)
        assert found is not None
        assert found['device'].startswith('/dev/video')
        assert threading.active_count() == orig_threads_num + 1

        _user_logged_in = (lambda: camera['nickname'] in
                           self._get_server_nicknames())
        self.wait_until(_user_logged_in)

    def test_post_invalid_camera(self):
        camera = dict(CameraFactory(), id=0, nickname=None)
        response = self.post(self._url, camera)
        assert response.code == 400
        assert 'id' in response.json['errors']
        assert 'nickname' in response.json['errors']

    def _get_server_nicknames(self):
        users = manager.src_client.users.values()
        nicknames = [str(user.nickname, 'utf8') for user in users]
        return nicknames
