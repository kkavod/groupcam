from time import sleep

from groupcam.core import logger, get_child_logger, options
from groupcam.tt4 import TT4, consts


COMPLETE_COMMANDS = {
    command: value
    for value, command in enumerate(
        ['complete_login', 'complete_join_channel'])
}


class BaseClient:
    _subscription = (
        consts.SUBSCRIBE_NONE |
        consts.SUBSCRIBE_USER_MSG |
        consts.SUBSCRIBE_CHANNEL_MSG |
        consts.SUBSCRIBE_BROADCAST_MSG |
        consts.SUBSCRIBE_AUDIO |
        consts.SUBSCRIBE_VIDEO |
        consts.SUBSCRIBE_DESKTOP
    )

    def __init__(self, server_config):
        self._stopped = False
        self._logger = get_child_logger(self.__class__.__name__)
        self._server_config = server_config
        self._tt4 = TT4(server_config)
        self._user_id = None
        self._status_mode = consts.STATUS_AVAILABLE
        self._commands = {}
        self._tt4.connect()

    def stop(self):
        self._stopped = True

    def run(self):
        while not self._stopped:
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

    def on_connection_lost(self, message=None):
        self._logger.error("Connection to server lost, reconnecting...")
        self.disconnect()
        sleep(5.)
        self.connect()

    def on_command_myself_logged_in(self, message):
        self._user_id = message.first_param
        self._logger.info("Logged in to server")

    def on_command_user_logged_in(self, message):
        self._tt4.unsubscribe(message.first_param, self._subscription)

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
                self.on_complete_join_channel()

    def on_command_error(self, message):
        self._logger.error("Error performing the command (error code {}"
                           .format(message.first_param))
        self._tt4.disconnect()

    def on_command_user_logged_out(self, message):
        pass

    def on_command_user_left(self, message):
        pass

    def on_complete_join_channel(self):
        self._logger.info("Joined the channel")

    def _process_message(self, message):
        code = message.code

        if options.debug:
            self._logger.debug("Got message with code {}".format(code))

        if code == consts.WM_TEAMTALK_CON_SUCCESS:
            self.on_connection_success(message)
        elif code == consts.WM_TEAMTALK_CON_FAILED:
            self.on_connection_failed(message)
        elif code == consts.WM_TEAMTALK_CON_LOST:
            self.on_connection_lost(message)
        elif code == consts.WM_TEAMTALK_CMD_MYSELF_LOGGEDIN:
            self.on_command_myself_logged_in(message)
        elif code == consts.WM_TEAMTALK_CMD_MYSELF_LOGGEDOUT:
            self.on_command_myself_logged_out(message)
        elif code == consts.WM_TEAMTALK_CMD_USER_LOGGEDIN:
            self.on_command_user_logged_in(message)
        elif code == consts.WM_TEAMTALK_USER_VIDEOFRAME:
            self.on_user_video_frame(message)
        elif code == consts.WM_TEAMTALK_CMD_PROCESSING:
            self.on_command_processing(message)
        elif code == consts.WM_TEAMTALK_CMD_ERROR:
            self.on_command_error(message)
        elif code == consts.WM_TEAMTALK_CMD_USER_LOGGEDOUT:
            self.on_command_user_logged_out(message)
        elif code == consts.WM_TEAMTALK_CMD_USER_LEFT:
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
