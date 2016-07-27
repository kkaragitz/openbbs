"""Client handling module. Sets up an environment for the current thread."""

import logging
import sys
import textwrap

from asciichan.database import Database
from asciichan.login import prompt
from asciichan.shell import shell


def curry_io(client, database, ip):
    """Creates curried functions for sending messages to and receiving text 
    from the currently connected client.
    """
    def send(string, end="\r\n"):
        try:
            message = "\r\n".join(textwrap.wrap(string, width=80))
            client.send((string + end).encode())
        except OSError:
            logging.warning("Could not send \"%s\" to client." % string)

    def receive():
        try:
            response = client.recv(1024).decode().strip()
            return response
        except (OSError, UnicodeDecodeError, AttributeError):
            logging.warning("Client connection has been interrupted.")
            close(client, database, ip)
            sys.exit(1)

    return send, receive


def close(client, database, ip):
    """Safely close data related to the current session."""
    client.close()
    database.close()
    logging.info("Connection to %s has been closed.", ip)


def handle(client, ip, config):
    """Primary BBS functionality. Creates an environment for the current 
    connection thread, then passes the client off to a shell instance.
    """
    database = Database(
        config.get("server", "database", fallback="database.db"),
        config.get("server", "operators", fallback="")
    )
    send, receive = curry_io(client, database, ip)
    send(config.get("messages", "motd", fallback="Welcome to Asciichan-BBS!"))
    send("There are %d posts on this BBS." % database.get_post_count())
    name, status = prompt(send, receive, client, database)
    banned = database.check_banned(name, ip) if name else None
    if banned:
        send("%s According to our records, you were posting as %s under\n"
             "the IP %s. Reason: %s" % (config.get("messages", "banned",
                                                   fallback="Banned!"),
                                        name, ip, banned))
        logging.info("%s attempted to login, but is banned." % name)
    elif not name:
        logging.info("%s exited at the login prompt." % ip)
    else:
        logging.info("%s logged in as %s. Session opened." % (ip, name))
        shell(send, receive, name, status, database, config)
    close(client, database, ip)

