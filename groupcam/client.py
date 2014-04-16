from time import sleep

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
from groupcam.user import User


class ClientManager:
    def run_async(self):
        cameras = list(db.sync.cameras.find())
        clients = [SourceClient(cameras)]
        for camera in cameras:
            clients.append(DestinationClient(camera))

        pool = ThreadPool(len(clients))
        _run_client = lambda inst: inst.run()
        pool.map_async(_run_client, clients)

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
        file_mask = (config['camera']['device_name_format']
                     .replace('{number}', '*'))
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
            result = (config['camera']['device_name_format']
                      .format(number=number))
        else:
            result = None
        raise tornado.gen.Return(result)


class SourceClient(BaseClient):
    def __init__(self, cameras):
        super().__init__(config['server']['source'])
        self._users = {}
        self._cameras = [Camera(camera) for camera in cameras]
        self._user_cameras = {}

    def on_command_user_logged_in(self, message):
        user_id = message.first_param
        subscription = self._subscription

        camera = self._get_user_camera(user_id)
        if camera is not None:
            subscription &= not consts.SUBSCRIBE_VIDEO
            self._users[user_id] = User(user_id, self._tt4)
            self._user_cameras[user_id] = camera

        self._tt4.unsubscribe(user_id, subscription)

    def on_user_video_frame(self, message):
        user = self._users[message.first_param]
        user.update(message.second_param)
        self._user_cameras[message.first_param].add_user(user)

    def on_command_user_left(self, message):
        user_id = message.first_param
        if user_id in self._user_cameras:
            self._user_cameras[user_id].remove_user(user_id)

    def _get_user_camera(self, user_id):
        if user_id == self._user_id:
            return None
        else:
            profile = self._tt4.get_user(user_id)
            nickname = str(profile.nickname, 'utf8')
            for camera in self._cameras:
                if camera.nick_regexp.match(nickname):
                    return camera


class DestinationClient(BaseClient):
    def __init__(self, camera):
        server_config = dict(config['server']['destination'],
                             nickname=camera['nickname'])
        super().__init__(server_config)
        self._device = camera['device']

    def run(self):
        # TODO: connect on device have been created instead of the timeout
        sleep(5.)
        super().run()

    def on_complete_join_channel(self):
        self._tt4.start_broadcast(self._device)
        self._status_mode |= consts.STATUS_VIDEOTX
        self._tt4.change_status(self._status_mode)
        self._logger.info("Broadcast started")


manager = ClientManager()
