from groupcam.core import logger
from groupcam.core import initialize
from groupcam.client import poll_clients


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Processing
    while True:
        poll_clients()

    logger.info("Finished.")
