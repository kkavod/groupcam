"""A very primitive factories framework.
"""

import itertools


class Factory(dict):
    """Base factory class.
    """
    counter = itertools.count()
    template = {}

    def __init__(self):
        instance = {}
        number = next(self.counter)
        for key, value in self.template.items():
            if isinstance(value, str):
                value = value.format(counter=number)
            elif isinstance(value, itertools.count):
                value = number
            instance[key] = value
        self.update(instance)


class CameraFactory(Factory):
    template = {
        'id': "camera-{counter}",
        'title': "Title {counter}",
        'nickname_regexp': 'some.*regexp',
    }
