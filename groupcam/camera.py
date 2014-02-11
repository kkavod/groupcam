import re

import fcntl

import v4l2

import cairo
import numpy

from groupcam.conf import config
from groupcam.core import fail_with_error
from groupcam.tt4 import tt4
from groupcam.user import User


class Camera:
    def __init__(self):
        self._users = {}

        self._video_config = config.get('video', {})
        regexp_string = self._video_config.get('nickname_regexp',
                                               '.*scandinavia.*')
        self._nickname_regexp = re.compile(regexp_string, re.IGNORECASE)
        self._width = self._video_config.get('width', 320)
        self._height = self._video_config.get('height', 240)
        self._title = self._video_config.get('title', "Groupcam")

        self._init_device()
        self._init_surface()

    def process_user_frame(self, user_id, frames_count):
        profile = tt4.get_user(user_id)
        nickname = str(profile.nickname, 'utf8')
        match = self._nickname_regexp.match(nickname)

        if match is not None:
            print('matched')
            user = self._users.get(user_id, User(user_id, profile.nickname))
            user.update() and self._update()

    def remove_user(self, user_id):
        if user_id in self._users:
            del self._users[user_id]
            self._update()

    def _init_device(self):
        device_name = self._video_config.get('device', '/dev/video1')
        self._device = open(device_name, 'wb')
#         if self._device < 0:
#             fail_with_error("Unable open {} for writing".format(device_name))
        self._capability = self._get_device_capability()
        self._set_device_format()

    def _init_surface(self):
        self._data = numpy.empty(
            self._width * self._height, dtype=numpy.int32)
        self._surface = cairo.ImageSurface.create_for_data(
            self._data, cairo.FORMAT_ARGB32,
            self._width, self._height, self._width * 4)
        self._context = cairo.Context(self._surface)
        self._context.scale(self._width, self._height)

    def _get_device_capability(self):
        capability = v4l2.v4l2_capability()
        ret_code = fcntl.ioctl(self._device, v4l2.VIDIOC_QUERYCAP, capability)
        if ret_code == -1:
            fail_with_error("Unable to get device capabilities")
        return capability

    def _set_device_format(self):
        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
        fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_RGB32
        fmt.fmt.pix.width = self._width
        fmt.fmt.pix.height = self._height
        fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE
        fmt.fmt.pix.bytesperline = fmt.fmt.pix.width * 4
        fmt.fmt.pix.sizeimage = fmt.fmt.pix.width * fmt.fmt.pix.height * 4
        fmt.fmt.pix.colorspace = v4l2.V4L2_COLORSPACE_SRGB
        ret_code = fcntl.ioctl(self._device, v4l2.VIDIOC_S_FMT, fmt)
        if ret_code == -1:
            fail_with_error("Unable to get device capabilities")

    def _update(self):
        self._draw_title()
        self._context.fill()
        self._device.write(self._data)

    def _draw_title(self):
        pattern = cairo.SolidPattern(0, 0, 1.)
        self._context.rectangle(0, 0, 1, 0.5)
        self._context.set_source(pattern)

    def __del__(self):
        self._device.close()


camera = Camera()
