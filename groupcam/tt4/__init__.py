from time import sleep

import os

import ctypes

from groupcam.conf import config
from groupcam.core import fail_with_error
from groupcam.tt4 import consts
from groupcam.tt4 import structs


_ttstr = lambda val: (val or '').encode('utf8')


class TT4:
    """TT4 API wrapper.
    """

    _all_instances = {}

    @classmethod
    def singleton(cls, config_name):
        if config_name in cls._all_instances:
            result = cls._all_instances[config_name]
        else:
            result = TT4(config['servers'][config_name])
            cls._all_instances[config_name] = result
        return result

    @classmethod
    def get_instance(cls, config_name):
        return cls._all_instances.get(config_name)

    def __init__(self, server_config):
        self._server_config = server_config
        self._library = self._get_library()
        self._instance = self._library.TT_InitTeamTalkPoll()

    def _get_library(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        library_path = os.path.join(base_path, 'misc/libTeamTalk4.so')
        return ctypes.cdll.LoadLibrary(library_path)

    def connect(self):
        flags = self._library.TT_GetFlags(self._instance)
        if flags & consts.ClientFlag.CLIENT_CONNECTION:
            return

        host = self._server_config['host']
        tcp_port = self._server_config['tcp_port']
        udp_port = self._server_config['udp_port']
        result = self._library.TT_Connect(self._instance,
                                          _ttstr(host),
                                          tcp_port, udp_port, 0, 0)
        if not result:
            fail_with_error("Unable to establish connection with the server")

    def is_connected(self):
        flags = self._library.TT_GetFlags(self._instance)
        return flags & consts.ClientFlag.CLIENT_CONNECTION

    def get_message(self):
        message = structs.TTMessage()
        wait_ms_ptr = ctypes.pointer(ctypes.c_int32(-1))
        ret_code = self._library.TT_GetMessage(
            self._instance, ctypes.pointer(message), wait_ms_ptr)
        result = None if ret_code <= 0 else message
        return result

    def login(self):
        nickname = _ttstr(self._server_config['nickname'])
        server_password = _ttstr(self._server_config['server_password'])
        user_name = _ttstr(self._server_config['user_name'])
        user_password = _ttstr(self._server_config['user_password'])

        result = self._library.TT_DoLogin(self._instance,
                                          nickname, server_password,
                                          user_name, user_password)
        if not result:
            fail_with_error("Login failed")
        else:
            return result

    def change_status(self, mode, message=""):
        self._library.TT_DoChangeStatus(self._instance,
                                        mode, _ttstr(message))

    def get_channel_id_from_path(self, path):
        channel_id = self._library.TT_GetChannelIDFromPath(self._instance,
                                                           _ttstr(path))
        if not channel_id:
            fail_with_error("Invalid channel path")
        return channel_id

    def join_channel_by_id(self, channel_id, channel_password=''):
        command_id = self._library.TT_DoJoinChannelByID(
            self._instance, channel_id, _ttstr(channel_password))

        if command_id <= 0:
            fail_with_error("Unable to join the channel")
        return command_id

    def get_user(self, user_id):
        user = structs.User()
        self._library.TT_GetUser(self._instance, user_id, ctypes.pointer(user))
        return user

    def get_user_video_format(self, user_id):
        video_format = structs.CaptureFormat()
        ret_code = self._library.TT_GetUserVideoFrame(
            self._instance, user_id, None, 0, ctypes.pointer(video_format))
        return bool(ret_code) and video_format

    def get_user_video_frame(self, user_id, data, bytes_number, video_format):
        format_ptr = ctypes.pointer(video_format)
        data_ptr = data.ctypes.data
        ret_code = self._library.TT_GetUserVideoFrame(
            self._instance, user_id, data_ptr, bytes_number, format_ptr)
        return bool(ret_code)

    def start_broadcast(self):
        device_id = self._find_device()
        self._init_capture_device(device_id)
        self._library.TT_EnableTransmission(self._instance,
                                            structs.TRANSMIT_VIDEO, True)

    def unsubscribe(self, user_id, subscriptions):
        self._library.TT_DoUnsubscribe(self._instance, user_id, subscriptions)

    def reconnect(self):
        self.disconnect()
        sleep(consts.RECONNECT_INTERVAL)
        self.connect()

    def disconnect(self):
        self._library.TT_Disconnect(self._instance)

    def _find_device(self):
        device_id = None

        device_number = ctypes.c_uint32()
        device_number_ptr = ctypes.pointer(device_number)

        self._library.TT_GetVideoCaptureDevices(self._instance,
                                                None, device_number_ptr)
        device_path = config['camera']['device']

        if device_number.value > 0:
            video_devices = (structs.VideoCaptureDevice *
                             device_number.value)()
            self._library.TT_GetVideoCaptureDevices(self._instance,
                                                    video_devices,
                                                    device_number_ptr)
            for index in range(device_number.value):
                device_id = str(video_devices[index].device_id, 'utf-8')
                if device_path == device_id.split(',')[0]:
                    break

        if device_id is None:
            fail_with_error("Device {} not found".format(device_path))

        return device_id

    def _init_capture_device(self, device_id):
        theora = structs.TheoraCodec(0, config['camera']['quality'])

        video_codec = structs.VideoCodec(
            structs.THEORA_CODEC,
            structs.VideoCodec._u(theora)
        )

        capture_format = structs.CaptureFormat(
            config['camera']['width'],
            config['camera']['height'],
            config['camera']['fps'],
            1,
            structs.FOURCC_RGB32
        )

        ret_code = self._library.TT_InitVideoCaptureDevice(
            self._instance,
            _ttstr(device_id),
            ctypes.pointer(capture_format),
            ctypes.pointer(video_codec)
        )

        if ret_code <= 0:
            fail_with_error("Unable to start broadcast")

    def __del__(self):
        self._library.TT_CloseTeamTalk(self._instance)
