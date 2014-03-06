from time import sleep

from multiprocessing import Pool

from groupcam.conf import config
from groupcam.core import logger, get_child_logger, options
from groupcam.tt4 import TT4
from groupcam.tt4.consts import StatusMode, ClientEvent
from groupcam.camera import Camera


def run_clients():
    """Module entry point.
    """

    pool = Pool(len(config['servers']))
    pool.map(_run_client, [SourceClient, DestinationClient])


def _run_client(cls):
    cls().run()


COMPLETE_COMMANDS = {
    command: value
    for value, command in enumerate(
        ['complete_login', 'complete_join_channel'])
}


class BaseClient:
    _config_name = None

    def __init__(self):
        self._logger = get_child_logger(self._config_name)
        self._server_config = config['servers'][self._config_name]
        self._tt4 = TT4.singleton(self._config_name)
        self._user_id = None
        self._status_mode = StatusMode.AVAILABLE
        self._commands = {}
        self._tt4.connect()

    def run(self):
        while True:
            message = self._tt4.get_message()
            if message is not None:
                self._process_message(message)

    def on_connection_success(self, message):
        command_id = self._tt4.login()
        self._commands[command_id] = (
            COMPLETE_COMMANDS['complete_login'])
        self._logger.info("Connected to server")

    def on_connection_failed(self, message):
        self._tt4.disconnect()
        self._logger.error("Failed to connect to server")

    def on_connection_lost(self, message):
        self._tt4.disconnect()
        self._logger.error("Connection to server lost, reconnecting...")
        sleep(1.)
        self._tt4.connect()

    def on_command_myself_logged_in(self, message):
        self._user_id = message.first_param
        self._logger.info("Logged in to server")

    def on_command_myself_logged_out(self, message):
        self._tt4.disconnect()
        self._logger.info("Logged out from server")

    def on_user_video_frame(self, message):
        pass

    def on_command_processing(self, message):
        command = self._commands.get(message.first_param)
        complete = bool(message.second_param)

        if command is not None and complete:
            if command == COMPLETE_COMMANDS['complete_login']:
                self._complete_login()
            elif command == COMPLETE_COMMANDS['complete_join_channel']:
                self._logger.info("Joined the channel")

    def on_command_error(self, message):
        self._logger.error("Error performing the command (error code {}"
                           .format(message.first_param))
        self._tt4.disconnect()

    def on_command_user_logged_out(self, message):
        pass

    def on_command_user_left(self, message):
        pass

    def _process_message(self, message):
        code = message.code

        if options.debug:
            self._logger.debug("Got message with code {}".format(code))

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
            self._logger.debug("Message with code {} is unknown".format(code))

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
    _config_name = 'source'

    def __init__(self):
        super().__init__()

        self._camera = Camera()

    def on_user_video_frame(self, message):
        if message.first_param != self._user_id:
            profile = self._tt4.get_user(message.first_param)
            nickname = str(profile.nickname, 'utf8')
            self._camera.process_user_frame(message.first_param,
                                            nickname,
                                            message.second_param)

    def on_command_user_left(self, message):
        self._camera.remove_user(message.first_param)


class DestinationClient(BaseClient):
    _config_name = 'destination'

    def __init__(self):
        super().__init__()
        self._broadcast_started = False

    def on_user_video_frame(self, message):
        # TODO: start broadcast in constructor after a delay
        if not self._broadcast_started:
            self._tt4.start_broadcast()
            self._status_mode |= StatusMode.VIDEOTX
            self._tt4.change_status(self._status_mode)
            self._logger.info("Broadcast started")
            self._broadcast_started = True
