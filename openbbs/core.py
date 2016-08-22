"""Primary entry point to the OpenBBS server process."""

import logging
import os
import socket
import sys
import threading

import daemon

from openbbs.cli import parser
from openbbs.config import load_config
from openbbs.session import handle


def spawn_server(config, debug=False):
    """Creates the server instance from given parameters."""
    backlog = int(config.get("backlog"))
    port = int(config.get("port"))
    host = config.get("host")
    if not host:
        host = socket.gethostbyname(socket.gethostname())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((host, port))
    except (OSError, socket.gaierror):
        logging.critical("Could not bind to %s:%s!", host, port)
        server.close()
        sys.exit(1)
    else:
        logging.info("Server successfully bound to %s:%s.", host, port)

    try:
        server.listen(backlog)
        while True:
            client, address = server.accept()
            ip_address = address[0]
            logging.info("Connection received from %s.", ip_address)
            connection_thread = threading.Thread(
                target=handle,
                args=(client, ip_address, config)
            )
            connection_thread.daemon = True
            connection_thread.start()
            if debug:
                server.close()
                break
    except KeyboardInterrupt:
        server.close()
        logging.info("Server shutting down...")


def main():
    """Primary entry point for OpenBBS. Parses the configuration file
    and command-line arguments to set up a server environment.
    """
    arguments = parser.parse_args()
    config = load_config(arguments.config)
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        filename=config.get("logfile")
    )

    if arguments.daemonize:
        context = daemon.DaemonContext()
        context.files_preseve = [arguments.config, config.get("database")]
        context.working_directory = os.getcwd()
        with context:
            spawn_server(config)
    else:
        spawn_server(config)

    logging.info("Server closed.")
