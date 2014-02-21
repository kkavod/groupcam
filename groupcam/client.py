from time import sleep

from groupcam.conf import config
from groupcam.core import logger, options
from groupcam.tt4 import TT4
from groupcam.tt4.consts import StatusMode, ClientEvent
from groupcam.camera import Camera
from groupcam.core import get_child_logger


_clients = []


def poll_clients():
    global _clients
    if not _clients:
        _clients += [SourceClient(), DestinationClient()]
    for client in _clients:
        client.poll()


COMPLETE_COMMANDS = {
    command: value
    for value, command in enumerate(
        ['complete_login', 'complete_join_channel'])
}


class BaseClient:
    def __init__(self, server_config):
        self._logger = None
        self._server_config = server_config
        self._tt4 = TT4(server_config)
        self._user_id = None
        self._status_mode = StatusMode.AVAILABLE
        self._commands = {}
        self._tt4.connect()

    def poll(self):
        message = self._tt4.get_message()
        code = message.code

        if options.debug:
            logger.debug("Got message with code {}".format(code))

        if code == ClientEvent.WM_TEAMTALK_CON_SUCCESS:
            self.on_connection_success(message)
        elif code == ClientEvent.WM_TEAMTALK_CON_FAILED:
            self.on_connection_failed(message)
        elif code == ClientEvent.WM_TEAMTALK_CON_LOST:
            self.on_connection_lost(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_MYSELF_LOGGEDIN:
            self.on_command_myself_logged_in(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_MYSELF_LOGGEDOUT:
            self.on_command_myself_logged_out(message)
        elif code == ClientEvent.WM_TEAMTALK_USER_VIDEOFRAME:
            self.on_user_video_frame(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_PROCESSING:
            self.on_command_processing(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_ERROR:
            self.on_command_error(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_USER_LOGGEDOUT:
            self.on_command_user_logged_out(message)
        elif code == ClientEvent.WM_TEAMTALK_CMD_USER_LEFT:
            self.on_command_user_left(message)
        else:
            logger.debug("Unknown message")

    def on_connection_success(self, message):
        command_id = self._tt4.login()
        self._commands[command_id] = (
            COMPLETE_COMMANDS['complete_login'])
        logger.info("Connected to server")

    def on_connection_failed(self, message):
        self._tt4.disconnect()
        logger.error("Failed to connect to server")

    def on_connection_lost(self, message):
        self._tt4.disconnect()
        logger.error("Connection to server lost, reconnecting...")
        sleep(1.)
        self._tt4.connect()

    def on_command_myself_logged_in(self, message):
        self._user_id = message.first_param
        logger.info("Logged in to server")

    def on_command_myself_logged_out(self, message):
        self._tt4.disconnect()
        logger.info("Logged out from server")

    def on_user_video_frame(self, message):
        pass

    def on_command_processing(self, message):
        command = self._commands.get(message.first_param)
        complete = bool(message.second_param)

        if command is not None and complete:
            if command == COMPLETE_COMMANDS['complete_login']:
                self._complete_login()
            elif command == COMPLETE_COMMANDS['complete_join_channel']:
                logger.info("Joined the channel")

    def on_command_error(self, message):
        logger.error("Error performing the command (error code {}"
                     .format(message.first_param))
        self._tt4.disconnect()

    def on_command_user_logged_out(self, message):
        pass

    def on_command_user_left(self, message):
        pass

    def _complete_login(self):
        self._tt4.change_status(self._status_mode)

        channel_path = self._server_config['channel_path']
        logger.info("Joining the channel {}...".format(channel_path))
        channel_id = self._tt4.get_channel_id_from_path(channel_path)

        channel_password = self._server_config['channel_password']
        command_id = self._tt4.join_channel_by_id(channel_id, channel_password)
        self._commands[command_id] = COMPLETE_COMMANDS['complete_join_channel']

    def __del__(self):
        self._tt4.disconnect()


class SourceClient(BaseClient):
    def __init__(self):
        super().__init__(config['servers']['source'])
        self._camera = Camera()
        self._logger = get_child_logger('source')

    def on_user_video_frame(self, message):
        if message.first_param != self._user_id:
            profile = self._tt4.get_user(self._user_id)
            nickname = str(profile.nickname, 'utf8')
            self._camera.process_user_frame(message.first_param,
                                            nickname,
                                            message.second_param)

    def on_command_user_left(self, message):
        self._camera.remove_user(message.first_param)


class DestinationClient(BaseClient):
    def __init__(self):
        super().__init__(config['servers']['destination'])
        self._logger = get_child_logger('source')
        self._tt4.start_broadcast()
