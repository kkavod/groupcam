import ctypes


# A struct containing the properties of an event.

# The event can be retrieved by called #TT_GetMessage. This
# struct is only required on non-Windows systems.

# Section @ref events explains event handling in the local client
# instance.

# See TT_GetMessage


class TTMessage(ctypes.Structure):
    _fields_ = [('code', ctypes.c_int),
                ('first_param', ctypes.c_uint32),
                ('second_param', ctypes.c_uint32)]
