"""Core functionality for the Asciichan server."""

import argparse
import configparser
import daemon
import logging
import os
import socket
import threading

import asciichan
import asciichan.session


class CustomHelp(argparse.HelpFormatter):
    """Small modifications argparse's default HelpFormatter."""
    def _fill_text(self, text, width, indent):
        return "".join(indent + line
                       for line in text.splitlines(keepends=True))

    def _split_lines(self, text, width):
        return text.splitlines()

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "Usage: "
        return super(CustomHelp, self).add_usage(usage, actions, groups,
                                                 prefix)


def spawn_server(config):
    """Creates the server instance from given parameters."""
    host = config.get("server", "host")
    port = int(config.get("server", "port"))
    backlog = int(config.get("server", "backlog"))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if host.lower() == "dynamic":
        temporary_socket = socket.socket()
        temporary_socket.connect(("184.72.106.52", 80))
        host = temporary_socket.getsockname()[0]
        temporary_socket.close()
    elif not host:
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


def parse_arguments():
    """Parse command-line arguments and return the namespace."""
    parser = argparse.ArgumentParser(
        add_help=False, formatter_class=CustomHelp,
        usage="%(prog)s [path/to/config.ini] [OPTIONS]",
        description=asciichan.__doc__)
    parser._positionals.title = 'Positional Arguments'
    parser._optionals.title = 'Optional Arguments'
    parser.add_argument("-h", "--help", action="help",
                        help="Display this help page and exit.")
    parser.add_argument(
        "-v", "--version", action="version",
        version="Asciichan Version %s." % asciichan.__version__,
        help="Display the currently installed version and exit."
    )
    parser.add_argument("-b", "--daemonize", action="store_true",
                        help="Run the server as a UNIX daemon. (Background "
                        "Process)")
    parser.add_argument("-c", "--config", metavar="XX", default="./config.ini",
                        help="Specify the path of the config.ini file that "
                        "the Asciichan\nserver should read from.")
    return parser.parse_args()


def main():
    """Primary entry point to the server, parses the configuration file and 
    sets up the server environment.
    """
    arguments = parse_arguments()
    config = configparser.ConfigParser()
    config.read(arguments.config)
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S",
                        level=logging.INFO,
                        filename=config.get("server", "logfile"))
    if arguments.daemonize:
        context = daemon.DaemonContext()
        context.files_preseve = [arguments.config, config.get("server",
                                                              "database")]
        context.working_directory = os.getcwd()
        with context:
            spawn_server(config)
    else:
        spawn_server(config)
    logging.info("Server closed.")
