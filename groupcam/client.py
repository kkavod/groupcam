import re

from multiprocessing import Pool

from groupcam.conf import config
from groupcam.tt4 import consts
from groupcam.tt4.client import BaseClient
from groupcam.camera import Camera


def run_clients_async():
    """Module entry point.
    """

    pool = Pool(len(config['servers']))
    pool.map_async(_run_client, [SourceClient, DestinationClient])


def _run_client(cls):
    cls().run()


class SourceClient(BaseClient):
    _config_name = 'source'

    def __init__(self):
        super().__init__()

        self._camera = Camera()
        regexp_string = config['camera']['nickname_regexp']
        self._nickname_regexp = re.compile(regexp_string, re.IGNORECASE)

    def on_command_user_logged_in(self, message):
        user_id = message.first_param
        subscription = self._subscription

        if self._user_match(user_id):
            subscription &= not consts.SUBSCRIBE_VIDEO

        self._tt4.unsubscribe(user_id, subscription)

    def on_user_video_frame(self, message):
        self._camera.process_user_frame(message.first_param,
                                        message.second_param)

    def on_command_user_left(self, message):
        self._camera.remove_user(message.first_param)

    def _user_match(self, user_id):
        if user_id == self._user_id:
            result = False
        else:
            profile = self._tt4.get_user(user_id)
            nickname = str(profile.nickname, 'utf8')
            result = bool(self._nickname_regexp.match(nickname))
        return result


class DestinationClient(BaseClient):
    _config_name = 'destination'

    def on_complete_join_channel(self):
        self._tt4.start_broadcast()
        self._status_mode |= consts.STATUS_VIDEOTX
        self._tt4.change_status(self._status_mode)
        self._logger.info("Broadcast started")
