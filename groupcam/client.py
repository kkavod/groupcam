from time import sleep

from groupcam.conf import config
from groupcam.core import logger
from groupcam.tt4 import tt4
from groupcam.tt4.consts import StatusMode, ClientEvent
from groupcam.camera import camera


COMPLETE_COMMANDS = {
    command: value
    for value, command in enumerate(
        ['complete_login', 'complete_join_channel'])
}


class Client:
    def __init__(self):
        self._user_id = None
        self._status_mode = StatusMode.AVAILABLE
        self._commands = {}
        tt4.connect()

    def run(self):
        while True:
            message = tt4.get_message()
            code = message.code

            if code == ClientEvent.WM_TEAMTALK_CON_SUCCESS:
                command_id = tt4.login()
                self._commands[command_id] = (
                    COMPLETE_COMMANDS['complete_login'])
                logger.info("Connected to server")
            elif code == ClientEvent.WM_TEAMTALK_CON_FAILED:
                tt4.disconnect()
                logger.error("Failed to connect to server")
            elif code == ClientEvent.WM_TEAMTALK_CON_LOST:
                tt4.disconnect()
                logger.error("Connection to server lost, reconnecting...")
                sleep(1.)
                tt4.connect()
            elif code == ClientEvent.WM_TEAMTALK_CMD_MYSELF_LOGGEDIN:
                self._user_id = message.first_param
                logger.info("Logged in to server")
            elif code == ClientEvent.WM_TEAMTALK_CMD_MYSELF_LOGGEDOUT:
                tt4.disconnect()
                logger.info("Logged out from server")
            elif code == ClientEvent.WM_TEAMTALK_USER_VIDEOFRAME:
                if message.first_param != self._user_id:
                    camera.process_user_frame(message.first_param,
                                              message.second_param)
            elif code == ClientEvent.WM_TEAMTALK_CMD_PROCESSING:
                self._process_command(message.first_param,
                                      bool(message.second_param))
            elif code == ClientEvent.WM_TEAMTALK_CMD_ERROR:
                logger.error("Error performing the command (error code {}"
                             .format(message.first_param))
                tt4.disconnect()
            elif code == ClientEvent.WM_TEAMTALK_CMD_USER_LOGGEDOUT:
                pass
            elif code == ClientEvent.WM_TEAMTALK_CMD_USER_LEFT:
                camera.remove_user(message.first_param)

    def _process_command(self, command_id, complete):
        command = self._commands.get(command_id)

        if command is not None and complete:
            if command == COMPLETE_COMMANDS['complete_login']:
                self._complete_login()
            elif command == COMPLETE_COMMANDS['complete_join_channel']:
                logger.info("Joined the channel")

    def _complete_login(self):
        tt4.change_status(self._status_mode)

        channel_path = config['server'].get('channel_path',
                                            '/unity/scandinavian')
        logger.info("Joining the channel {}...".format(channel_path))
        channel_id = tt4.get_channel_id_from_path(channel_path)

        channel_password = config['server'].get('channel_password')
        command_id = tt4.join_channel_by_id(channel_id, channel_password)
        self._commands[command_id] = COMPLETE_COMMANDS['complete_join_channel']

    def __del__(self):
        tt4.disconnect()
