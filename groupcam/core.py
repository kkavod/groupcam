import sys

import argparse

import logging


__description__ = ""
__version__ = "0.01"


__all__ = ['options', 'logger', 'initialize', 'get_child_logger',
           'fail_with_error']


options = argparse.Namespace()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('groupcam')

argparser = argparse.ArgumentParser(description=__description__)


def initialize():
    """Initializes the core.

    @param config_path: config path string
    """
    from groupcam.conf import load_config

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

    argparser.parse_args(namespace=options)

    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Switched to debug mode")

    load_config(options.config)


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

    sys.exit(-1)
