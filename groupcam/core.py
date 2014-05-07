import os
import sys

import signal

import argparse

import logging


__description__ = "Unites individual cameras into one groupcam"
__version__ = "0.1"


__all__ = ['options', 'logger', 'initialize', 'get_child_logger',
           'fail_with_error']


options = argparse.Namespace()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('groupcam')

# Exit function to call on failure
_exit_func = lambda: sys.exit(-1)


def initialize(testing=False):
    """Initializes the core.

    @param config_path: config path string
    """

    from groupcam.conf import load_config
    from groupcam.db import init_database

    argparser = argparse.ArgumentParser(description=__description__)

    # Adding common options to argparser

    argparser.add_argument('--verbose', action="store_true",
                           dest='verbose',
                           help="force verbose output")
    argparser.add_argument('-d', '--debug', action="store_true",
                           dest='debug', default=False,
                           help="enable debug mode")
    argparser.add_argument('-t', '--traceback', action="store_true",
                           dest='traceback',
                           help="dump traceback on errors")
    argparser.add_argument('-v', '--version', action="version",
                           version=__version__,
                           help="print program version")
    argparser.add_argument('-c', '--config', dest='config',
                           help="config file path")

    argparser.parse_args(args=[] if testing else None, namespace=options)

    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Switched to debug mode")

    signal.signal(signal.SIGINT, _exit_func)

    if testing:
        conf_path = get_project_path('misc/testing.yaml')
    else:
        conf_path = options.config

    load_config(conf_path)
    init_database()


def get_child_logger(suffix):
    """Returns new core logger's descendant with the same logging level.

    @param suffix: suffix string
    """
    child = logger.getChild(suffix)
    child.setLevel(logger.level)

    return child


def fail_with_error(message):
    """Prints the error message and terminates the program execution.

    @param message: error message
    """

    exc_info = getattr(options, 'traceback', False) and any(sys.exc_info())
    logger.critical(message, exc_info=exc_info)

    _exit_func()


def get_project_path(relative_path):
    """Returns absolute path constructed from a relative path under
    the current project.

    @param relative_path: project sub-path
    """

    base_path = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.join(base_path, relative_path)
    return project_path
