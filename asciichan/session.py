"""Client handling module. Sets up an environment for the current thread."""

import logging

import asciichan.database
import asciichan.shell


def curry_io(client):
    """Creates curried functions for sending messages to and receiving text 
    from the currently connected client.
    """
    def send(string):
        try:
            client.send(string.encode())
        except OSError:
            logging.warning("Could not send \"%s\" to client." % string)
    def receive():
        try:
            response = client.recv(1024).decode().strip()
            return response
        except (OSError, UnicodeDecodeError):
            logging.warning("Could not get message from client.")
    return send, receive


def handle(client, ip, config):
    """Primary BBS functionality. Creates an environment for the current 
    connection thread, then passes the client off to a shell instance.
    """
    send, receive = curry_io(client)
    database = asciichan.database.Database(config.get("server", "database"),
                                           config.get("server", "operators"))
    send(config.get("messages", "motd"))
    send("\nThere are %d posts on this BBS.\n" % database.get_post_count())
    name, status = asciichan.shell.login(send, receive, client, database)
    banned = database.check_banned(name, ip) if name else None
    if banned:
        send("%s According to our records, you were posting as %s under\n"
             "the IP %s. Reason: %s\n" % (config.get("messages", "banned"),
                                          name, ip, banned))
        logging.info("%s attempted to login, but is banned." % name)
    elif not name:
        logging.info("%s exited at the login prompt." % ip)
    else:
        logging.info("%s logged in as %s. Session opened." % (ip, name))
        asciichan.shell.shell(send, receive, name, status, database, config)
    database.close()
    client.close()
    logging.info("Connection to %s has been closed." % ip)

