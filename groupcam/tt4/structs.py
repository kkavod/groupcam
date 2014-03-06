import ctypes


# The length of a string (characters, not bytes) which is used to
# extract information from this DLL.
#
# If a string is passed to the client instance is longer than
# TT_STRLEN it will be truncated.
#
# On Windows the client instance converts unicode characters to
# UTF-8 before transmission, so be aware of non-ASCII characters
# if communicating with the TeamTalk server from another
# applications than the TeamTalk client.
TT_STRLEN = 512

#  The maximum number of video formats which will be queried
#  for a VideoCaptureDevice.
TT_CAPTUREFORMATS_MAX = 128


# Enum specifying data transmission types
TransmitType = ctypes.c_uint
(
    TRANSMIT_NONE,
    TRANSMIT_AUDIO,
    TRANSMIT_VIDEO,
) = list(range(3))


# The codecs supported.
Codec = ctypes.c_uint
(
    NO_CODEC,
    SPEEX_CODEC,
    CELT_0_5_2_OBSOLETE_CODEC,
    THEORA_CODEC,
    SPEEX_VBR_CODEC,
    CELT_CODEC,
    CELT_VBR_CODEC,
) = list(range(7))

# The picture format used by a capture device.
FourCC = ctypes.c_uint
(
    FOURCC_NONE,
    FOURCC_I420,
    FOURCC_YUY2,
    FOURCC_RGB32,
) = [0, 100, 101, 102]


class TheoraCodec(ctypes.Structure):
    _fields_ = [
        ('target_bitrate', ctypes.c_int32),
        ('quality', ctypes.c_int32),
    ]


class VideoCodec(ctypes.Structure):
    class _u(ctypes.Union):
        _fields_ = [
            ('theora', TheoraCodec),
        ]

    _fields_ = [
        ('codec', Codec),
        ('param', _u),
    ]


class CaptureFormat(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_int32),
        ('height', ctypes.c_int32),
        ('fps_numerator', ctypes.c_int32),
        ('fps_denominator', ctypes.c_int32),
        ('four_cc', FourCC),
    ]


class VideoCaptureDevice(ctypes.Structure):
    _fields_ = [
        ('device_id', ctypes.c_char * TT_STRLEN),
        ('device_name', ctypes.c_char * TT_STRLEN),
        ('capture_api', ctypes.c_char * TT_STRLEN),
        ('capture_formats', CaptureFormat * TT_CAPTUREFORMATS_MAX),
        ('capture_formats_count', ctypes.c_int32),
    ]


class TTMessage(ctypes.Structure):
    """A struct containing the properties of an event.

    The event can be retrieved by called #TT_GetMessage. This
    struct is only required on non-Windows systems.

    Section events explains event handling in the local client
    instance.

    See TT_GetMessage()
    """

    _fields_ = [('code', ctypes.c_int),
                ('first_param', ctypes.c_uint32),
                ('second_param', ctypes.c_uint32)]


class User(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_int32),
        ('nickname', ctypes.c_char * TT_STRLEN),
        ('username', ctypes.c_char * TT_STRLEN),
        ('status_mode', ctypes.c_int32),
        ('status_message', ctypes.c_char * TT_STRLEN),
        ('channel_id', ctypes.c_int32),
        ('ip_address', ctypes.c_char * TT_STRLEN),
        ('version', ctypes.c_char * TT_STRLEN),
        ('user_type', ctypes.c_uint32),
        ('user_state', ctypes.c_uint32),
        ('local_subscriptions', ctypes.c_uint32),
        ('peer_subscriptions', ctypes.c_uint32),
        ('user_data', ctypes.c_int32),
        ('audio_folder', ctypes.c_char * TT_STRLEN),
        ('audio_file_format', ctypes.c_uint32),
        ('audio_file_name', ctypes.c_char * TT_STRLEN),
    ]
