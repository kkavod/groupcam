import re

from datetime import datetime

import fcntl

import v4l2

import cairo

import numpy
from math import sqrt

from groupcam.conf import config
from groupcam.core import options, fail_with_error
from groupcam.tt4 import tt4
from groupcam.user import User


class Camera:
    def __init__(self):
        self._users = {}

        self._load_settings()
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

    def _load_settings(self):
        regexp_string = config['video']['nickname_regexp']
        self._nickname_regexp = re.compile(regexp_string, re.IGNORECASE)
        self._width = config['video']['width']
        self._height = config['video']['height']
        self._title = config['video']['title']
        self._title_filling = 1. - config['video']['title_padding'] / 100.
        self._title_height = (self._height *
                              config['video']['title_height'] / 100.)
        self._padding = config['video']['user_padding'] / 100. * self._height

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

    def _get_device_capability(self):
        capability = v4l2.v4l2_capability()
        ret_code = fcntl.ioctl(self._device, v4l2.VIDIOC_QUERYCAP, capability)
        if ret_code == -1:
            fail_with_error("Unable to get device capabilities")
        return capability

    def _set_device_format(self):
        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
        fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_BGR32
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
        self._draw_background()
        self._update_users()
        self._draw_users()
        self._device.write(self._data)

    def _draw_title(self):
        self._context.set_source_rgb(0, 0, 1.)
        self._context.rectangle(0, 0, self._width, self._title_height)
        self._context.fill()

        self._context.set_font_size(self._height)
        text_width, text_height = self._context.text_extents(self._title)[2:4]

        factor = min(self._width * self._title_filling / text_width,
                     self._title_height * self._title_filling / text_height)
        font_size = self._height * factor
        self._context.set_font_size(font_size)

        left = self._width - (self._width + text_width * factor) / 2
        top = (self._title_height -
               (self._title_height - text_height * factor) / 2)
        self._context.move_to(left, top)
        self._context.set_source_rgb(1., 1., 1.)
        self._context.show_text(self._title)

    def _draw_background(self):
        self._context.set_source_rgb(0, 0, 0)
        self._context.rectangle(0, self._title_height,
                                self._width, self._height)
        self._context.fill()

    def _draw_users(self):
        for user in self._users.values():
            self._context.save()
            left, top, width, height = user.display_rect
            self._context.translate(left, top)
            self._context.scale(width / user.img_width,
                                height / user.img_height)
            self._context.set_source_surface(user.surface)
            self._context.paint()
            self._context.restore()

            if options.debug:
                self._draw_user_labels(left, top, str(user.user_id))

    def _draw_user_labels(self, left, top, label):
        font_size = self._height * 0.05
        self._context.set_font_size(font_size)
        self._context.move_to(left, top + font_size)
        self._context.set_source_rgb(0.4, 1., 0.4)
        self._context.show_text(label)

    def _update_users(self):
        display_width = self._width
        display_height = self._height - self._title_height - self._padding * 2

        aspect_ratio = self._width / self._height
        pixels_total = self._width * display_height / (.5 + len(self._users))

        user_width = round(sqrt(pixels_total * aspect_ratio))
        user_height = round(sqrt(pixels_total / aspect_ratio))

        cols_number = round(display_width / user_width)
        rows_number = round(display_height / user_height)

        if cols_number * user_width > display_width:
            user_width = display_width / cols_number
            user_height = user_width / aspect_ratio

        if rows_number * user_height > display_height:
            user_height = display_height / rows_number
            user_width = user_height * aspect_ratio

        left = self._width - (display_width + user_width * cols_number) / 2
        top = (self._height -
               (display_height + user_height * rows_number) / 2 - self._padding)

        sort_key = lambda user: user.nickname
        users = sorted(self._users.values(), key=sort_key)
        for index, user in enumerate(users):
            x = left + (index % cols_number * user_width)
            y = top + int(index / cols_number) * user_height + self._padding
            user.display_rect = (x, y,
                                 user_width - self._padding,
                                 user_height - self._padding)
            self._remove_user_if_dead(user)

    def _remove_user_if_dead(self, user):
        seconds = (datetime.now() - user.updated).seconds
        if seconds > config['video']['user_timeout']:
            del self._users[user.user_id]

    def __del__(self):
        self._device.close()
