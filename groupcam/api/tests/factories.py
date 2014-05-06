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


class FactoryList(Factory):
    def __init__(self, factory, min_count=0, max_count=0):
        self._factory = factory
        self._min_count = min_count
        self._max_count = max_count

    def __call__(self):
        return [self._factory()
                for index in range(self._min_count, self._max_count)]


class RandomChoice(Factory):
    def __init__(self, values):
        self._values = values

    def __call__(self):
        return random.choice(self._values)


class Counter(Factory):
    def __init__(self, start=0):
        self.counter = itertools.count(start)

    def __call__(self):
        return next(self.counter)


class PresetFactory(Factory):
    template = {
        'number': Counter(),
        'name': "Preset {counter}",
        'type': RandomChoice(['5+1', '3x3', '4x4']),
        'layout': {
            '0': "Aaron",
            '1': "Abdul",
            '2': "Abdullah",
            '3': "Abel",
            '4': "Abraham",
            '5': "Abram",
        },
        'active': False,
    }


class CameraFactory(Factory):
    template = {
        'id': "camera-{counter}",
        'title': "Title {counter}",
        'nickname': "Nickname {counter}",
        'regexp': 'some.*regexp',
        'presets': FactoryList(PresetFactory, 1, 7),
    }
