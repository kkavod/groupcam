import numpy

from datetime import datetime

from groupcam.tt4 import tt4


class User:
    def __init__(self, user_id, nickname):
        self.user_id = user_id
        self.nickname = nickname
        self._updated = datetime.now()
        self._data = None

    def update(self):
        video_format = tt4.get_user_video_format(self.user_id)
        if not video_format:
            return

        return True

    def _init_surface(self, width, height):
        self._data = numpy.empty(
            width * height, dtype=numpy.int32)
