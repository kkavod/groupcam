import numpy
import cairo

from datetime import datetime

from groupcam.tt4 import TT4


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.surface = None
        self.img_width = self.img_height = 0
        self.display_rect = (0, 0, 0, 0)
        self.updated = datetime.now()
        self._tt4 = TT4.get_instance('source')
        self._data = None

    def update(self, frames_count=1):
        video_format = self._tt4.get_user_video_format(self.user_id)
        if not video_format:
            return

        if (self._data is None or
                self.img_width != video_format.width or
                self.img_height != video_format.height):
            self._init_surface(video_format)

        for index in range(frames_count):
            result = self._tt4.get_user_video_frame(
                self.user_id, self._data, len(self._data) * 4, video_format)
        if result:
            self.updated = datetime.now()
        return True

    def _init_surface(self, video_format):
        self.img_width = video_format.width
        self.img_height = video_format.height
        self._data = numpy.empty(self.img_width * self.img_height,
                                 dtype=numpy.int32)

        self.surface = cairo.ImageSurface.create_for_data(
            self._data, cairo.FORMAT_ARGB32, self.img_width, self.img_height)
