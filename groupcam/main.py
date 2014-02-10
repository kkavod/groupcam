from groupcam.core import logger
from groupcam.core import initialize
from groupcam.client import Client


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Processing
    Client().run()

    logger.info("Finished.")
