import os

from ctypes import cdll

from groupcam.conf import config
from groupcam.core import fail_with_error
from groupcam.tt4 import consts


class TT4:
    """TT4 API wrapper.
    """

    def __init__(self):
        self._library = self._get_library()
        self._instance = self._library.TT_InitTeamTalkPoll()

    def _get_library(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        library_path = os.path.join(base_path, 'misc/libTeamTalk4.so')
        return cdll.LoadLibrary(library_path)

    def connect(self):
        flags = self._library.TT_GetFlags(self._instance)
        if flags & consts.CLIENT_CONNECTION:
            return

        server_config = config.get('server', {})
        host = server_config.get('host', 'unity.kbb1.com')
        tcp_port = server_config.get('tcp_port', 10333)
        udp_port = server_config.get('udp_port', 10333)
        result = self._library.TT_Connect(self._instance,
                                          host.encode('utf8'),
                                          tcp_port, udp_port, 0, 0)
        if not result:
            fail_with_error("Unable to establish connection with the server")

    def disconnect(self):
        self._instance.TT_Disconnect(self._instance)

    def __del__(self):
        self._library.TT_CloseTeamTalk(self._instance)


tt4 = TT4()
