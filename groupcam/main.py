from groupcam.core import logger
from groupcam.core import initialize
from groupcam.client import run_clients


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Processing
    run_clients()

    logger.info("Finished.")
