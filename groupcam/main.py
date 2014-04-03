from groupcam.core import initialize
from groupcam.client import manager
from groupcam.api.main import run_http_server


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Clients
    manager.run_async()

    # RESTful API
    run_http_server()
