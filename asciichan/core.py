"""Primary entry point to the Asciichan server process."""

import logging
import os
import socket
import sys
import threading

import daemon

from asciichan.cli import parser
from asciichan.config import curry_configuration
from asciichan.session import handle


def spawn_server(config_get, debug=False):
    """Creates the server instance from given parameters."""
    host = config_get("server", "host", default=None)
    port = int(config_get("server", "port", default=1337))
    backlog = int(config_get("server", "backlog", default=5))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allows for the server to easily be stopped and restarted.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not host:
        host = socket.gethostbyname(socket.gethostname())

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
            ip = address[0]
            logging.info("Connection received from %s.", ip)
            # Python2 does not support daemon in Thread's __init__.
            connection_thread = threading.Thread(
                target=handle,
                args=(client, ip, config_get)
            )
            connection_thread.daemon = True
            connection_thread.run()
            if debug:
                server.close()
                break
    except KeyboardInterrupt:
        server.close()
        logging.info("Server shutting down...")


def main():
    """Primary entry point for Asciichan. Parses the configuration file
    and command-line arguments to set up a server environment.
    """
    arguments = parser.parse_args()
    config_get = curry_configuration(arguments.config)
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        filename=config_get("server", "logfile", default=None)
    )

    if arguments.daemonize:
        context = daemon.DaemonContext()
        context.files_preseve = [
            arguments.config,
            config_get("server", "database", default="database.db")
        ]
        context.working_directory = os.getcwd()
        with context:
            spawn_server(config_get)

    else:
        spawn_server(config_get)

    logging.info("Server closed.")
