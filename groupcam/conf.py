import os

import yaml

from .core import fail_with_error


# Global configuration dictionary
config = {}


def load_config(config_path):
    """Loads YAML configuration file.

    @param config_path: config path
    """

    if config_path is None or not os.path.exists(config_path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, 'misc/config.yaml')

    with open(config_path) as config_file:
        try:
            cfg = yaml.load(config_file)
        except IOError:
            fail_with_error("Config file not found ({0})".format(config_path))
        except yaml.YAMLError:
            fail_with_error("Error parsing {0}, specify --traceback option "
                            "for details".format(config_path))
        config.update(cfg)
