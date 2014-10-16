from datetime import datetime
import re
import os
import fcntl
import ctypes

import v4l2
import cairo
import numpy

from groupcam.conf import config
from groupcam.core import options, fail_with_error
from groupcam.preset import preset_factory


class Camera:
    def __init__(self, camera):
        self._users = {}

        self._camera = camera
        self._lib = self._get_v4l2_lib()
        self._load_settings()
        self._init_device()
        self._init_surface()
        self._set_initial_preset()

    def add_user(self, user):
        self._users[user.user_id] = user

    def remove_user(self, user_id):
        if user_id in self._users:
            del self._users[user_id]
            self._update()

    def update_if_has_user(self, user_id):
        if user_id in self._users:
            self._update()

    def activate_preset(self, preset):
        self._preset = preset_factory(self, preset)
        self._update()

    def _get_v4l2_lib(self):
        try:
            lib = ctypes.cdll.LoadLibrary('libv4l2.so.0')
        except OSError:
            fail_with_error("Unable to load libv4l2, is it installed?")
        return lib

    def _load_settings(self):
        self._title_padding = config['camera']['title_padding'] / 100.
        self.width = config['camera']['width']
        self.height = config['camera']['height']
        self.aspect_ratio = self.width / self.height
        self.title_height = (self.height *
                             config['camera']['title_height'] / 100.)
        self.padding = config['camera']['user_padding'] / 100. * self.height
        self.display_width = self.width
        self.display_height = (self.height
                               - self.title_height
                               - self.padding * 2)
        self.nick_regexp = re.compile(self._camera['regexp'], re.IGNORECASE)

    def _init_device(self):
        self._device_fd = None
        device_name = self._camera['device']
        device_name_buf = device_name.encode('utf8')
        self._device_fd = self._lib.v4l2_open(device_name_buf, os.O_RDWR)
        if self._device_fd == -1:
            fail_with_error("Unable to open device {}".format(device_name))
        self._capability = self._get_device_capability()
        self._set_device_format()

    def _init_surface(self):
        self._data = numpy.empty(
            self.width * self.height, dtype=numpy.int32)
        self._surface = cairo.ImageSurface.create_for_data(
            self._data, cairo.FORMAT_ARGB32,
            self.width, self.height, self.width * 4)
        self._context = cairo.Context(self._surface)

    def _get_device_capability(self):
        capability = v4l2.v4l2_capability()
        ret_code = fcntl.ioctl(self._device_fd,
                               v4l2.VIDIOC_QUERYCAP, capability)
        if ret_code == -1:
            fail_with_error("Unable to get device capabilities")
        return capability

    def _set_device_format(self):
        fmt = v4l2.v4l2_format()
        fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
        fmt.fmt.pix.pixelformat = v4l2.V4L2_PIX_FMT_BGR32
        fmt.fmt.pix.width = self.width
        fmt.fmt.pix.height = self.height
        fmt.fmt.pix.field = v4l2.V4L2_FIELD_NONE
        fmt.fmt.pix.bytesperline = fmt.fmt.pix.width * 4
        fmt.fmt.pix.sizeimage = fmt.fmt.pix.width * fmt.fmt.pix.height * 4
        fmt.fmt.pix.colorspace = v4l2.V4L2_COLORSPACE_SRGB
        ret_code = fcntl.ioctl(self._device_fd, v4l2.VIDIOC_S_FMT, fmt)
        if ret_code == -1:
            fail_with_error("Unable to get device capabilities")

    def _update(self):
        self._draw_title()
        self._draw_background()
        self._draw_users() or self._draw_no_users()
        os.write(self._device_fd, self._data)

    def _draw_title(self):
        self._context.set_source_rgb(0, 0, 1.)
        self._context.rectangle(0, 0, self.width, self.title_height)
        self._context.fill()

        horizontal_padding = self.width * self._title_padding
        vertical_padding = self.title_height * self._title_padding
        title_rect = (horizontal_padding, vertical_padding,
                      self.width - horizontal_padding * 2,
                      self.title_height - vertical_padding * 2)
        self._fit_text_to_rect(self._camera['title'], title_rect)

    def _draw_background(self):
        self._context.set_source_rgb(0, 0, 0)
        self._context.rectangle(0, self.title_height,
                                self.width, self.height)
        self._context.fill()

    def _draw_no_users(self):
        message = config['camera']['no_users_message']
        display_rect = (self.width * 0.1, self.title_height,
                        self.width * 0.8, self.height - self.title_height)
        self._fit_text_to_rect(message, display_rect)

    def _draw_users(self):
        alive_users = [user for user in self._users.values()
                       if self._user_is_alive(user)]
        display_rects = self._preset.get_user_display_rects(alive_users)
        for user, display_rect in display_rects:
            self._draw_user(user, display_rect)
        return bool(alive_users)

    def _draw_user(self, user, display_rect):
        self._context.save()
        left, top, width, height = display_rect
        self._context.translate(left, top)
        self._context.scale(width / user.img_width,
                            height / user.img_height)
        self._context.set_source_surface(user.surface)
        self._context.paint()
        self._context.restore()

        self._draw_user_label(user, left, top, width, height)

    def _draw_user_label(self, user, left, top, width, height):
        label_rect = (width / 3., 0, width * 2 / 3., height * 0.15)
        label_left, label_top, label_width, label_height = label_rect

        self._context.set_source_rgb(0, 0, 1.)
        self._context.rectangle(label_left, 0, label_width, label_height)
        self._context.fill()

        self._fit_text_to_rect(user.label.upper(), label_rect)

    def _user_is_alive(self, user):
        if user.updated is None:
            result = False
        else:
            seconds = (datetime.now() - user.updated).seconds
            result = seconds <= config['camera']['user_timeout']
        return result

    def _fit_text_to_rect(self, text, rect, color=(1., 1., 1.)):
        rect_left, rect_top, rect_width, rect_height = rect

        self._context.set_font_size(self.height)
        text_width, text_height = self._context.text_extents(text)[2:4]

        factor = min(rect_width / text_width, rect_height / text_height)
        font_size = self.height * factor
        self._context.set_font_size(font_size)

        left = rect_left + rect_width - (rect_width + text_width * factor) / 2
        top = rect_top + rect_height - (rect_height - text_height * factor) / 2

        self._context.move_to(left, top)
        self._context.set_source_rgb(*color)
        self._context.show_text(text)

    def _set_initial_preset(self):
        active_presets = [preset for preset in self._camera['presets']
                          if preset['active']]
        if active_presets:
            active_preset = active_presets[0]
        else:
            active_preset = dict(type='auto', layout={})
        self.activate_preset(active_preset)

    def __del__(self):
        self._lib.v4l2_close(self._device_fd)
