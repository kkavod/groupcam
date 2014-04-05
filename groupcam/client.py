import re

import glob

from multiprocessing import Pool

import motor

import tornado.gen

from groupcam.conf import config
from groupcam.db import db
from groupcam.tt4 import consts
from groupcam.tt4.client import BaseClient
from groupcam.camera import Camera


class ClientManager:
    _clients = {}

    def run_async(self):
        def _run(cls):
            cls().run()

        pool = Pool(len(config['server']))
        pool.map_async(_run, [SourceClient, DestinationClient])

    @tornado.gen.engine
    def add(self, camera):
        camera['device'] = self._find_free_device()
        yield motor.Op(db.async.cameras.insert, camera)

    def update(self, camera):
        pass

    def remove(self, id):
        pass

    def _parse_device_intervals(self):
        range_from, range_to = self._find_device_ranges()
        intervals = config['camera']['device_intervals']
        splitted = map(str.strip, intervals.split(','))
        splitted_twice = (interval.split('-') for interval in splitted)
        numbers = set()
        for interval in splitted_twice:
            number_from = int(interval[0] or range_from)
            number_to = int(interval[-1] or range_to) + 1
            for number in range(number_from, number_to):
                numbers.add(number)
        return list(numbers)

    def _find_device_ranges(self):
        devices = glob.glob('/dev/video*')
        return [1, 9]

    def _find_free_device(self):
        cursor = db.async.cameras.find(fields=['device'])
        cameras = yield motor.Op(cursor.to_list)


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


manager = ClientManager()
