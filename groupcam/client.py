from time import sleep

import re

import glob

from threading import Thread
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
    def __init__(self):
        self._run_client = lambda inst: inst.run()

    def run_async(self):
        cameras = list(db.sync.cameras.find())
        self.src_client = SourceClient(cameras)
        self.dest_clients = []
        for camera in cameras:
            self.dest_clients.append(DestinationClient(camera))

        clients = [self.src_client] + self.dest_clients
        pool = ThreadPool(len(clients))
        pool.map_async(self._run_client, clients)

    @tornado.gen.coroutine
    def add(self, camera):
        camera['device'] = yield self._find_free_device()
        yield motor.Op(db.async.cameras.insert, camera)
        client = DestinationClient(camera)
        self.dest_clients.append(client)
        thread = Thread(target=self._run_client, args=[client])
        thread.start()

    def update(self, camera):
        pass

    def remove(self, id):
        pass

    def get_camera(self, camera_id):
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
        self._cameras = {
            camera['id']: Camera(camera)
            for camera in cameras
        }

    def on_command_user_logged_in(self, message):
        user_id = message.first_param
        user = User(user_id, self._tt4)
        self._users[user_id] = user

        subscription = self._subscription
        cameras = self._get_user_cameras(user_id)
        if cameras:
            [camera.add_user(user) for camera in cameras]
            subscription &= not consts.SUBSCRIBE_VIDEO

        self._tt4.unsubscribe(user_id, subscription)

    def on_user_video_frame(self, message):
        user = self._users[message.first_param]
        user.update(message.second_param)
        assert user.img_width > 0
        assert user.img_height > 0
        for camera in self._cameras.values():
            camera.update_if_has_user(user.user_id)

    def on_command_user_left(self, message):
        # TODO: immidiately hide user on leaving the channel
        # user = self._users[message.first_param]
        # user.hide()
        pass

    def _get_user_cameras(self, user_id):
        if user_id == self._user_id:
            cameras = []
        else:
            profile = self._tt4.get_user(user_id)
            nickname = str(profile.nickname, 'utf8')
            cameras = [
                camera for camera in self._cameras.values()
                if camera.nick_regexp.match(nickname)
            ]
        return cameras


class DestinationClient(BaseClient):
    def __init__(self, camera):
        server_config = dict(config['server']['destination'],
                             nickname=camera['nickname'])
        super().__init__(server_config)
        self._device = camera['device']

    def run(self):
        # TODO: connect on device has been created instead of the timeout
        # sleep(5.)
        super().run()

    def on_complete_join_channel(self):
        self._tt4.start_broadcast(self._device)
        self._status_mode |= consts.STATUS_VIDEOTX
        self._tt4.change_status(self._status_mode)
        self._logger.info("Broadcast started")


manager = ClientManager()
