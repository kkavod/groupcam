from groupcam.core import logger
from groupcam.core import initialize
from groupcam.client import Client


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Processing
    source_client = Client()
    while True:
        source_client.poll()

    logger.info("Finished.")
