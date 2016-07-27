"""Core functionality for the Asciichan server."""

import configparser
import logging
import os
import socket
import sys
import threading

import daemon

from asciichan.cli import parser
from asciichan.session import handle


def spawn_server(config):
    """Creates the server instance from given parameters."""
    host = config.get("server", "host", fallback="127.0.0.1")
    port = config.getint("server", "port", fallback=1337)
    backlog = config.getint("server", "backlog", fallback=5)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not host:
        host = socket.gethostbyname(socket.gethostname())
    try:
        server.bind((host, port))
    except OSError:
        logging.critical("Could not bind to %s:%s!" % (host, port))
        sys.exit(1)
    logging.info("Server successfully bound to %s:%s." % (host, port))
    server.listen(backlog)
    try:
        while True:
            client, address = server.accept()
            ip = address[0]
            logging.info("Connection received from %s." % ip)
            threading.Thread(
                name="Connection %s" % ip,
                target=handle,
                daemon=True,
                args=(client, ip, config)
            ).start()
    except KeyboardInterrupt:
        server.close()
        logging.info("Server shutting down...")


def main():
    """Primary entry point for Asciichan. Parses the configuration file
    and command-line arguments to set up a server environment.
    """
    arguments = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(arguments.config)
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S",
                        level=logging.INFO,
                        filename=config.get("server", "logfile",
                                            fallback=None))
    if arguments.daemonize:
        context = daemon.DaemonContext()
        context.files_preseve = [
            arguments.config,
            config.get("server", "database", fallback="database.db")
        ]
        context.working_directory = os.getcwd()
        with context:
            spawn_server(config)
    else:
        spawn_server(config)
    logging.info("Server closed.")
