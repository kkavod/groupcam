"""A very primitive factories framework.
"""

import random
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
            elif isinstance(value, Factory):
                value = value()
            instance[key] = value
        self.update(instance)


class PresetFactory(Factory):
    template = {
        'number': "{counter}",
        'name': "Preset {counter}",
        # 'type': FactoryLazy(["5+1", "3x3", "4x4"]),
        'layout': {
            0: "Aaron",
            1: "Abdul",
        },
        'active': False,
    }


class CameraFactory(Factory):
    template = {
        'id': "camera-{counter}",
        'title': "Title {counter}",
        'nickname': "Nickname {counter}",
        'regexp': 'some.*regexp',
        'presets': [],
    }
