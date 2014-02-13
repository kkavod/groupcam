import collections

import os

import yaml

from groupcam.core import fail_with_error


# Global configuration dictionary
config = {}


def load_config(config_path=None):
    """Loads YAML configuration file.

    @param config_path: config path
    """

    defaults = _load_defaults()
    if config_path is not None:
        custom_config = _load_custom_config(config_path)
        _deep_update(defaults, custom_config)
    config.update(defaults)


def _load_defaults():
    base_path = os.path.dirname(os.path.abspath(__file__))
    defaults_path = os.path.join(base_path, 'misc/defaults.yaml')
    with open(defaults_path) as defaults_file:
        defaults = yaml.load(defaults_file)
    return defaults


def _load_custom_config(config_path):
    with open(config_path) as config_file:
        try:
            custom_config = yaml.load(config_file)
        except IOError:
            fail_with_error("Config file not found ({})".format(config_path))
        except yaml.YAMLError:
            fail_with_error("Error parsing {}, specify --traceback option "
                            "for details".format(config_path))
    return custom_config


def _deep_update(dest, src):
    for key, value in src.items():
        if isinstance(value, collections.Mapping):
            dest_val = dest.get(key, {})
            dest[key] = _deep_update(dest_val, value)
        else:
            dest[key] = src[key]
    return dest
