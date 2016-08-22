"""Client handling module. Sets up an environment for the current thread."""

import logging
import socket
import sys
import textwrap

from openbbs.database import Database
from openbbs.login import prompt
from openbbs.shell import shell


class UserSession(object):
    """Abstraction of Socket's client send/recv, encapsulates
    user-specific data such as the database instance and the user's
    name.
    """
    def __init__(self, client, database, ip_address):
        self.client = client
        self.database = database
        self.ip_address = ip_address

        self.current_board = "main"
        self.current_thread = None

    def send(self, message, end="\r\n"):
        """Friendlier wrapper for socket's client.send."""
        try:
            self.client.send((message + end).encode())
        except (OSError, socket.error):
            logging.warning("Could not send \"%s\" to client.", message)

    def receive(self):
        """Friendlier wrapper for socket's client.recv."""
        try:
            return self.client.recv(1024).decode().strip()
        except (OSError, UnicodeDecodeError, AttributeError):
            logging.warning("Client connection has been interrupted.")
            self.close()

    def close(self):
        """Safe cleanup for all client and database instances owned by
        the user's current thread. Also hangs up the thread.
        """
        self.client.close()
        self.database.close()
        logging.info("Connection to %s has been closed.", self.ip_address)
        sys.exit(0)


def handle(client, ip_address, config):
    """Primary BBS functionality. Creates an environment for the current
    connection thread, then passes the client off to a shell instance.
    """
    database = Database(config.get("database"), config.get("operators"))
    user = UserSession(client, database, ip_address)

    user.send(config.get("motd"))
    user.send("There are %d posts right now." % database.get_post_count())
    user.name, user.status = prompt(user)

    banned = database.check_banned(user.name, ip_address)
    if banned:
        user.send("%s Reason: %s" % (config.get("banned"), ip_address, banned))
        logging.info("%s attempted to login, but is banned.", user.name)
    else:
        logging.info("%s logged in as %s.", ip_address, user.name)
        shell(user, config)

    user.close()
