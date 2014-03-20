import ctypes


from groupcam.tt4 import consts


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
        ('codec', consts.Codec),
        ('param', _u),
    ]


class CaptureFormat(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_int32),
        ('height', ctypes.c_int32),
        ('fps_numerator', ctypes.c_int32),
        ('fps_denominator', ctypes.c_int32),
        ('four_cc', consts.FourCC),
    ]


class VideoCaptureDevice(ctypes.Structure):
    _fields_ = [
        ('device_id', ctypes.c_char * consts.TT_STRLEN),
        ('device_name', ctypes.c_char * consts.TT_STRLEN),
        ('capture_api', ctypes.c_char * consts.TT_STRLEN),
        ('capture_formats', CaptureFormat * consts.TT_CAPTUREFORMATS_MAX),
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
        ('nickname', ctypes.c_char * consts.TT_STRLEN),
        ('username', ctypes.c_char * consts.TT_STRLEN),
        ('status_mode', ctypes.c_int32),
        ('status_message', ctypes.c_char * consts.TT_STRLEN),
        ('channel_id', ctypes.c_int32),
        ('ip_address', ctypes.c_char * consts.TT_STRLEN),
        ('version', ctypes.c_char * consts.TT_STRLEN),
        ('user_type', ctypes.c_uint32),
        ('user_state', ctypes.c_uint32),
        ('local_subscriptions', ctypes.c_uint32),
        ('peer_subscriptions', ctypes.c_uint32),
        ('user_data', ctypes.c_int32),
        ('audio_folder', ctypes.c_char * consts.TT_STRLEN),
        ('audio_file_format', ctypes.c_uint32),
        ('audio_file_name', ctypes.c_char * consts.TT_STRLEN),
    ]
