from groupcam.core import logger, options
from groupcam.core import initialize, fail_with_error
from groupcam.conf import config

from groupcam.tt4 import tt4


def main():
    """Groupcam runner entry point function.
    """

    # Groupcam runner specific arguments
#     argparser.add_argument('movie', metavar='MOVIE',
#                            help='A movie file to play')

    # Initializing the core
    initialize()

    # Processing
    tt4.connect()
    logger.info("Finished.")
