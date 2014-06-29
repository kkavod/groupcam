import collections

import yaml

from groupcam.core import fail_with_error, get_project_path


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
    defaults_path = get_project_path('misc/defaults.yaml')
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
