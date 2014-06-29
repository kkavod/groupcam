from groupcam.client import manager
from groupcam.api.tests.base import BaseAPITestCase


class TestUsers(BaseAPITestCase):
    def test_get_users(self):
        resp = self.get('/users')
        assert resp.code == 200
        tt4_users = [str(user.nickname, 'utf8')
                     for user in manager.src_client.users.values()]
        assert len(tt4_users) > 0
        api_users = [user['name'] for user in
                     resp.json['users']]
        assert set(tt4_users) == set(api_users)
