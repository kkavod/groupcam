# Interval in ms
POLL_INTERVAL = 25

WM_USER = 0


class StatusMode:
    AVAILABLE = 0x00000000
    AWAY = 0x00000001
    QUESTION = 0x00000002
    MODE = 0x000000FF
    FLAGS = 0xFFFFFF00
    FEMALE = 0x00000100
    VIDEOTX = 0x00000200
    DESKTOP = 0x00000400
    STREAM_MEDIAFILE = 0x00000800


class ClientFlag:
    """
    Flags used to describe the the client instance current
    state.

    The client's state is a bitmask of the flags in #ClientFlag.

    The state of the client instance can be retrieved by calling
    #TT_GetFlags. This enables the user application to display the
    possible options to the end user. If e.g. the flag
    #CLIENT_AUTHORIZED is not set it will not be possible to
    perform any other commands except #TT_DoLogin. Doing so will
    make the server return an error message to the client.
    """

    # The client instance (#TTInstance) is in closed
    # state, i.e. #TT_InitTeamTalk has return a valid instance
    # ready for use but no operations has been performed on
    # it.
    CLIENT_CLOSED = 0x00000000

    # If set the client instance's sound input device has
    # been initialized, i.e. #TT_InitSoundInputDevice has been
    # called successfully.
    CLIENT_SNDINPUT_READY = 0x00000001

    # If set the client instance's sound output device
    # has been initialized, i.e. #TT_InitSoundOutputDevice has
    # been called successfully.
    CLIENT_SNDOUTPUT_READY = 0x00000002

    # If set the client instance's video device has been
    # initialized, i.e. #TT_InitVideoCaptureDevice has been
    # called successfuly.
    CLIENT_VIDEO_READY = 0x00000004

    # If set the client instance current have an active
    # desktop session, i.e. TT_SendDesktopWindow() has been
    # called. Call TT_CloseDesktopWindow() to close the desktop
    # session.
    CLIENT_DESKTOP_ACTIVE = 0x00000008

    # If set the client instance will start transmitting
    # audio if the sound level is above the voice activation
    # level. The event #WM_TEAMTALK_VOICE_ACTIVATION is posted
    # when voice activation initiates transmission,
    # see TT_SetVoiceActivationLevel and TT_EnableVoiceActivation
    CLIENT_SNDINPUT_VOICEACTIVATED = 0x00000010

    # If set the client instance will try to remove noise
    # from recorded audio, see TT_EnableDenoising
    CLIENT_SNDINPUT_DENOISING = 0x00000020

    # If set the client instance is using automatic gain
    # control, see TT_EnableAGC
    CLIENT_SNDINPUT_AGC = 0x00000040

    # If set the client instance has muted all users,
    # see TT_SetSoundOutputMute
    CLIENT_SNDOUTPUT_MUTE = 0x00000080

    # If set the client instance will auto position users
    # in a 180 degree circle using 3D-sound. This option is only
    # available with #SOUNDSYSTEM_DSOUND, see TT_SetUserPosition
    # and TT_Enable3DSoundPositioning
    CLIENT_SNDOUTPUT_AUTO3DPOSITION = 0x00000100

    # If set the client instance will try to eliminate
    # echo from speakers. To enable echo cancellation first make
    # the client run on sound duplex mode by calling
    # TT_InitSoundDuplexDevices() and afterwards call
    # TT_EnableEchoCancellation().
    CLIENT_SNDINPUT_AEC = 0x00000200

    # If set the client instance is running in sound
    # duplex mode where multiple audio output streams are mixed
    # into a single stream. This option must be enabled to
    # support echo cancellation (#CLIENT_SNDINPUT_AEC). Call
    # TT_InitSoundDuplexDevices() to enable duplex mode.
    CLIENT_SNDINOUTPUT_DUPLEX = 0x00000400

    # If set the client instance is currently transmitting
    # audio, see TT_EnableTransmission
    CLIENT_TX_AUDIO = 0x00001000

    # If set the client instance is currently transmitting video,
    # see TT_EnableTransmission
    CLIENT_TX_VIDEO = 0x00002000

    # If set the client instance is currently muxing
    # audio streams into a single file. This is enabled by calling
    # TT_StartRecordingMuxedAudioFile().
    CLIENT_MUX_AUDIOFILE = 0x00004000

    # If set the client instance is currently transmitting
    # a desktop window. A desktop window update is issued by calling
    # TT_SendDesktopWindow(). The event
    # #WM_TEAMTALK_DESKTOPWINDOW_TRANSFER is triggered when a desktop
    # window transmission completes.
    CLIENT_TX_DESKTOP = 0x00008000

    # If set the client instance is currently try to
    # connect to a server, i.e. #TT_Connect has been called.
    CLIENT_CONNECTING = 0x00010000

    # If set the client instance is connected to a server
    # i.e. #WM_TEAMTALK_CON_SUCCESS event has been issued after
    # doing a #TT_Connect. Valid commands in this state:
    # #TT_DoLogin
    CLIENT_CONNECTED = 0x00020000

    # Helper for #CLIENT_CONNECTING and #CLIENT_CONNECTED
    # to see if #TT_Disconnect should be called.
    CLIENT_CONNECTION = CLIENT_CONNECTING | CLIENT_CONNECTED

    # If set the client instance is logged on to a
    # server, i.e. got #WM_TEAMTALK_CMD_MYSELF_LOGGEDIN event
    # after issueing #TT_DoLogin.
    CLIENT_AUTHORIZED = 0x00040000

    # If set the client instance will try and connect to
    # other users using peer to peer connections. Audio will be
    # broadcast to users instead of forwarded through server
    # (thereby increasing the bandwith usage).  Note that if
    # #USERRIGHT_FORWARD_AUDIO is disabled and no peer to peer
    # connection could be established, i.e. event
    # #WM_TEAMTALK_CON_P2P was posted with failure, then data
    # cannot be transferred to a user.
    CLIENT_P2P_AUDIO = 0x00100000

    # If set the client instance will try and connect to
    # other users using peer to peer connections. Video will be
    # broadcast to users instead of forwarded through server
    # (thereby increasing the bandwith usage).  Note that if
    # #USERRIGHT_FORWARD_VIDEO is disabled and no peer to peer
    # connection could be established, i.e. event
    # #WM_TEAMTALK_CON_P2P was posted with failure, then data
    # cannot be transferred to a user.
    CLIENT_P2P_VIDEO = 0x00200000

    # Helper for #CLIENT_P2P_AUDIO and #CLIENT_P2P_VIDEO to see
    # if the client instance is currently attempting P2P connections.
    CLIENT_P2P = CLIENT_P2P_AUDIO | CLIENT_P2P_VIDEO

    # If set the client is currently streaming the audio
    # of a media file. When streaming a video file the
    # #CLIENT_STREAM_VIDEO flag is also typically set,
    # see TT_StartStreamingMediaFileToChannel()
    CLIENT_STREAM_AUDIO = 0x00400000

    # If set the client is currently streaming the video
    # of a media file. When streaming a video file the

    #CLIENT_STREAM_AUDIO flag is also typically set,
    # see TT_StartStreamingMediaFileToChannel()
    CLIENT_STREAM_VIDEO = 0x00800000


class ClientEvent:
    (WM_TEAMTALK_CON_SUCCESS,
     WM_TEAMTALK_CON_FAILED,
     WM_TEAMTALK_CON_LOST,
     WM_TEAMTALK_CON_P2P,
     WM_TEAMTALK_CMD_PROCESSING,
     WM_TEAMTALK_CMD_MYSELF_LOGGEDIN,
     WM_TEAMTALK_CMD_MYSELF_LOGGEDOUT,
     WM_TEAMTALK_CMD_MYSELF_JOINED,
     WM_TEAMTALK_CMD_MYSELF_LEFT,
     WM_TEAMTALK_CMD_MYSELF_KICKED,
     WM_TEAMTALK_CMD_USER_LOGGEDIN,
     WM_TEAMTALK_CMD_USER_LOGGEDOUT,
     WM_TEAMTALK_CMD_USER_UPDATE,
     WM_TEAMTALK_CMD_USER_JOINED,
     WM_TEAMTALK_CMD_USER_LEFT,
     WM_TEAMTALK_CMD_USER_TEXTMSG,
     WM_TEAMTALK_CMD_CHANNEL_NEW,
     WM_TEAMTALK_CMD_CHANNEL_UPDATE,
     WM_TEAMTALK_CMD_CHANNEL_REMOVE,
     WM_TEAMTALK_CMD_SERVER_UPDATE,
     WM_TEAMTALK_CMD_FILE_NEW,
     WM_TEAMTALK_CMD_FILE_REMOVE,
     WM_TEAMTALK_CMD_ERROR,
     WM_TEAMTALK_CMD_SUCCESS,
     WM_TEAMTALK_USER_TALKING,
     WM_TEAMTALK_USER_VIDEOFRAME,
     WM_TEAMTALK_USER_AUDIOFILE,
     WM_TEAMTALK_INTERNAL_ERROR,
     WM_TEAMTALK_VOICE_ACTIVATION,
     WM_TEAMTALK_STREAM_AUDIOFILE_USER,
     WM_TEAMTALK_STREAM_AUDIOFILE_CHANNEL,
     WM_TEAMTALK_HOTKEY,
     WM_TEAMTALK_HOTKEY_TEST,
     WM_TEAMTALK_FILETRANSFER,
     WM_TEAMTALK_USER_AUDIOBLOCK,
     WM_TEAMTALK_USER_DESKTOPWINDOW,
     WM_TEAMTALK_DESKTOPWINDOW_TRANSFER,
     WM_TEAMTALK_USER_DESKTOPCURSOR,
     WM_TEAMTALK_CON_MAX_PAYLOAD_UPDATED,
     WM_TEAMTALK_STREAM_MEDIAFILE_CHANNEL,) = [
         (WM_USER + index + 450) for index in range(40)]
