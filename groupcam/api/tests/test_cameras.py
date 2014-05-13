import threading

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

    def test_post_camera(self):
        orig_threads_num = threading.active_count()
        url = self.application.reverse_url('cameras')
        camera = CameraFactory()
        response = self.post(url, camera)
        assert response.code == 201
        assert response.json['ok'] is True
        del camera['presets']
        found = db.sync.cameras.find_one(camera)
        assert found is not None
        assert found['device'].startswith('/dev/video')
        assert threading.active_count() == orig_threads_num + 1

        _user_logged_in = (lambda: camera['nickname'] in
                           self._get_server_nicknames())

        def _user_logged_in():
            users = manager.src_client.users.values()
            nicknames = [str(user.nickname, 'utf8') for user in users]
            result = camera['nickname'] in nicknames
            return result

        self.wait_until(_user_logged_in)

    @pytest.mark.xfail
    def test_post_invalid_camera(self):
        assert False

    def _get_server_nicknames(self):
        users = manager.src_client.users.values()
        nicknames = [str(user.nickname, 'utf8') for user in users]
        return nicknames
