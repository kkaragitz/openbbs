"""Login prompt for the BBS."""

import time

import asciichan.database


def prompt(send, receive, client, database):
    """Provides the connected client with a login prompt, from which they can 
    log into an existing account, create a new one, or choose to browse 
    anonymously.
    """
    send("=" * 23 + "\r\nPLEASE SELECT AN OPTION\r\n" + "=" * 23
         + "\r\nLOGIN\t\tLogin to an existing account.\r\nREGISTER\tCreate a "
         "new account onthis BBS.\r\nANONYMOUS\tUse the BBS anonymously.\r\n"
         "QUIT\t\tExit the BBS.")
    while True:
        send("--> ", end="")
        command = receive().lower()
        if command == "login":
            send("USERNAME: ", end="")
            name = receive().lower()
            send("PASSWORD: ", end="")
            password = receive().encode()
            status, last_login = database.attempt_login(name, password)
            if status and last_login:
                send("Successfully logged in as %s.\r\nLast Login: %s.\r\n"
                     "Posts since then: %d.\r\nYou have %d new messages." %
                     (name, time.ctime(last_login),
                      database.get_post_count(last_login=last_login),
                      database.get_pm_count(name)))
                break
            else:
                send("Invalid login credentials.")
        elif command == "register":
            send("USERNAME: ", end="")
            name = receive().lower()
            status = "sysop" if name in database.operators else "user"
            send("PASSWORD: ", end="")
            password = receive()
            send("CONFIRM PASSWORD: ", end="")
            if receive() != password:
                send("Passwords do not match.")
                continue
            elif database.create_user(name, password.encode()):
                send("Account successfully created: %s." % name)
                break
            else:
                send("Account already exists.")
        elif command == "anonymous":
            name = "Anonymous"
            send("Don't make trouble...")
            status = "coward"
            break
        elif command == "quit":
            name = status = None
            break
        else:
            send("Invalid command \"%s\"." % command)
    return name, status
