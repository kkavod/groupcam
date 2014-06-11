import operator
from math import sqrt


class BasePreset:
    def __init__(self, camera, layout):
        self._camera = camera
        self._layout = layout

    def get_user_display_rects(self, users):
        """Calculates bounding rectangles to draw users according to
        current preset.

        @param users: list of User objects
        @return: list of rectangles
        """
        raise NotImplementedError


class AutoPreset:
    """The very basic preset, fits all given users into the frame.
    """

    def get_user_display_rects(self, users):
        display_rects = []

        display_area = self._self._display_width * self._display_height
        pixels_total = display_area / (.5 + len(users))

        user_width = round(sqrt(pixels_total * self._camera.aspect_ratio))
        user_height = round(sqrt(pixels_total / self._camera.aspect_ratio))

        cols_number = round(self._camera.display_width / user_width)
        rows_number = round(self._camera.display_height / user_height)

        if cols_number * user_width > self._camera.display_width:
            user_width = self._camera.display_width / cols_number
            user_height = user_width / self._camera.aspect_ratio

        if rows_number * user_height > self._camera.display_height:
            user_height = self._camera.display_height / rows_number
            user_width = user_height * self._camera.aspect_ratio

        horiz_middle = (self._display_width + user_width * cols_number) / 2
        vert_middle = (self._display_height + user_height * rows_number) / 2
        left = self._camera.display_width - horiz_middle
        top = self._camera.height - vert_middle

        users = sorted(users, key=operator.attrgetter('user_id'))
        for index, user in enumerate(users):
            x = left + (index % cols_number * user_width)
            y = top + int(index / cols_number) * user_height
            display_rect = (x, y,
                            user_width - self._camera.padding,
                            user_height - self._camera.padding)
            display_rects.append((user, display_rect))
        return display_rects


PRESETS = {
    'auto': AutoPreset,
}


def preset_factory(display_size, preset):
    return PRESETS[preset['type']](display_size, preset['layout'])
