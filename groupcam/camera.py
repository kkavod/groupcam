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

        regexp_string = config['video']['nickname_regexp']
        self._nickname_regexp = re.compile(regexp_string, re.IGNORECASE)
        self._width = config['video']['width']
        self._height = config['video']['height']
        self._title = config['video']['title']

        self._init_device()
        self._init_surface()

    def process_user_frame(self, user_id, frames_count):
        profile = tt4.get_user(user_id)
        nickname = str(profile.nickname, 'utf8')
        match = self._nickname_regexp.match(nickname)

        if match is not None:
            if user_id in self._users:
                user = self._users[user_id]
            else:
                user = User(user_id, profile.nickname)
                self._users[user_id] = user
            user.update() and self._update()

    def remove_user(self, user_id):
        if user_id in self._users:
            del self._users[user_id]
            self._update()

    def _init_device(self):
        device_name = config['video']['device']
        try:
            self._device = open(device_name, 'wb')
        except FileNotFoundError:
            fail_with_error("Unable open {} for writing".format(device_name))
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
        self._update_users()
        self._draw_users()
        self._device.write(self._data)

    def _draw_title(self):
        self._context.set_source_rgb(1., 0, 0)
        self._context.rectangle(0, 0, 1, 0.16)
        self._context.fill()
        self._context.set_font_size(0.14)
        self._context.move_to(0, 0.14)
        self._context.set_source_rgb(1., 1., 1.)
        self._context.show_text(self._title)

    def _draw_users(self):
        sort_key = lambda user: user.nickname
        users = sorted(self._users.values(), key=sort_key)
        for user in users:
            self._context.save()
            self._context.set_source_surface(user.image_surface)
            self._context.move_to(user.top, user.bottom)
            self._context.scale(user.width, user.height)
            self._context.paint()
            self._context.restore()

    def _update_users(self):
        padding = config['video']['user_padding'] / 100.

    def __del__(self):
        self._device.close()
