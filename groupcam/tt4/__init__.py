import os

import ctypes

from groupcam.conf import config
from groupcam.core import fail_with_error
from groupcam.tt4 import consts
from groupcam.tt4 import structs


class TT4:
    """TT4 API wrapper.
    """

    def __init__(self):
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

        server_config = config['server']
        host = server_config.get('host', 'unity.kbb1.com')
        tcp_port = server_config.get('tcp_port', 10333)
        udp_port = server_config.get('udp_port', 10333)
        result = self._library.TT_Connect(self._instance,
                                          host.encode('utf8'),
                                          tcp_port, udp_port, 0, 0)
        if not result:
            fail_with_error("Unable to establish connection with the server")

    def get_message(self):
        message = structs.TTMessage()
        wait_ms_ptr = ctypes.pointer(ctypes.c_int32(-1))
        result = self._library.TT_GetMessage(
            self._instance, ctypes.pointer(message), wait_ms_ptr)
        if not result:
            fail_with_error("Failed to get a message")
        return message

    def login(self):
        server_config = config['server']
        nickname = server_config.get('nickname', "Groupcam").encode('utf8')
        server_password = server_config.get(
            'server_password', "malhut").encode('utf8')
        user_name = server_config.get('user_name', '').encode('utf8')
        user_password = server_config.get('user_password', '').encode('utf8')

        result = self._library.TT_DoLogin(self._instance,
                                          nickname, server_password,
                                          user_name, user_password)
        if not result:
            fail_with_error("Login failed")
        else:
            return result

    def change_status(self, mode, message=""):
        self._library.TT_DoChangeStatus(self._instance,
                                        mode, message.encode('utf8'))

    def get_channel_id_from_path(self, path):
        channel_id = self._library.TT_GetChannelIDFromPath(self._instance,
                                                           path.encode('utf8'))
        if not channel_id:
            fail_with_error("Invalid channel path")
        return channel_id

    def join_channel_by_id(self, channel_id, channel_password=''):
        channel_password = (channel_password or '').encode('utf8')
        command_id = self._library.TT_DoJoinChannelByID(
            self._instance, channel_id, channel_password)

        if command_id <= 0:
            fail_with_error("Unable to join the channel")
        return command_id

    def get_user(self, user_id):
        user = structs.User()
        self._library.TT_GetUser(self._instance, user_id, ctypes.pointer(user))
        return user

    def disconnect(self):
        self._library.TT_Disconnect(self._instance)

    def __del__(self):
        self._library.TT_CloseTeamTalk(self._instance)


tt4 = TT4()
