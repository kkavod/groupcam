from groupcam.core import initialize
from groupcam.client import run_clients_async
from groupcam.api.main import run_http_server


def main():
    """Groupcam runner entry point function.
    """

    # Initializing the core
    initialize()

    # Processing
    run_clients_async()

    # RESTful API
    run_http_server()
