"""Core functionality for the Asciichan server."""

import configparser
import logging
import os
import socket
import threading

import daemon

import asciichan.session


def spawn_server(config):
    """Creates the server instance from given parameters."""
    host = config.get("server", "host")
    port = int(config.get("server", "port"))
    backlog = int(config.get("server", "backlog"))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if not host:
        host = socket.gethostbyname(socket.gethostname())
    try:
        server.bind((host, port))
    except OSError:
        logging.critical("Could not bind to %s:%s!" % (host, port))
        return
    logging.info("Server successfully bound to %s:%s." % (host, port))
    server.listen(backlog)
    try:
        while True:
            client, address = server.accept()
            ip = address[0]
            logging.info("Connection received from %s." % ip)
            threading.Thread(name="Connection %s" % ip,
                             target=asciichan.session.handle,
                             daemon=True,
                             args=(client, ip, config)).start()
    except KeyboardInterrupt:
        server.close()
        logging.info("Server exited.")


def main(arguments):
    """Parses the configuration file and sets up the server environment."""
    config = configparser.ConfigParser()
    config.read(arguments.config)
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S",
                        level=logging.INFO,
                        filename=config.get("server", "logfile"))
    if arguments.daemonize:
        context = daemon.DaemonContext()
        context.files_preseve = [arguments.config,
                                 config.get("server", "database")]
        context.working_directory = os.getcwd()
        with context:
            spawn_server(config)
    else:
        spawn_server(config)
    logging.info("Server closed.")
