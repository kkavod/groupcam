import re

import glob

from multiprocessing.pool import ThreadPool

import motor

import tornado.gen

from groupcam.conf import config
from groupcam.core import fail_with_error
from groupcam.db import db
from groupcam.tt4 import consts
from groupcam.tt4.client import BaseClient
from groupcam.camera import Camera


class ClientManager:
    _clients = {}

    def run_async(self):
        self._dev_name_format = config['camera']['device_name_format']

        clients = [SourceClient]
        cameras = db.sync.cameras.find()
#          for camera in cameras:
#              self._clients[camera['id']] = 

        def _run_client(inst):
            inst.run()

        pool = ThreadPool(len(cameras.count() + 1))
        # pool.map_async(_run_client, [SourceClient, DestinationClient])
        pool.map(_run_client, [SourceClient, DestinationClient])

    @tornado.gen.engine
    def add(self, camera):
        camera['device'] = yield self._find_free_device()
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
        file_mask = self._dev_name_format.replace('{number}', '*')
        devices = glob.glob(file_mask)
        numbers = sorted(self._get_numbers_from_devices(devices))
        if not numbers:
            fail_with_error("No video devices found!")
        return numbers[0], numbers[-1]

    def _get_numbers_from_devices(self, devices):
        numbers = []
        for device in devices:
            found = re.findall(r'\d+', device)
            if found:
                numbers.append(int(found[0]))
        return numbers

    @tornado.gen.coroutine
    def _find_free_device(self):
        possible_numbers = set(self._parse_device_intervals())
        cursor = db.async.cameras.find(fields=['device'])
        devices = yield motor.Op(cursor.to_list)
        occupied_numbers = set(self._get_numbers_from_devices(devices))
        available_numbers = possible_numbers - occupied_numbers
        if available_numbers:
            number = min(available_numbers)
            result = self._dev_name_format.format(number=number)
        else:
            result = None
        raise tornado.gen.Return(result)


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
