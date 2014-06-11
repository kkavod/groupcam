import operator
from math import sqrt


class BasePreset:
    def __init__(self, layout):
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

        display_width = self._width
        display_height = self._height - self._title_height - self._padding * 2

        aspect_ratio = self._width / self._height
        display_area = self._width * display_height
        pixels_total = display_area / (.5 + len(users))

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

        horizontal_middle = (display_width + user_width * cols_number) / 2
        vertical_middle = (display_height + user_height * rows_number) / 2
        left = self._width - horizontal_middle
        top = self._height - vertical_middle - self._padding

        users = sorted(users, key=operator.attrgetter('user_id'))
        for index, user in enumerate(users):
            x = left + (index % cols_number * user_width)
            y = top + int(index / cols_number) * user_height + self._padding
            display_rect = (x, y,
                            user_width - self._padding,
                            user_height - self._padding)
            display_rects.append((user, display_rect))
        return display_rects


PRESETS = {
    'auto': AutoPreset,
}


def preset_factory(preset):
    return PRESETS[preset['type']](preset['layout'])
