"""Login prompt for the BBS."""

import time


# Theoretically, the return could be removed and tests would only need to be
# tweaked a small bit to check for user.name and user.status rather than
# prompt's return value.
def prompt(user):
    """Provides the connected client with a login prompt, from which they can
    log into an existing account, create a new one, or choose to browse
    anonymously.
    """
    user.send("=======================\r\nPLEASE SELECT AN OPTION\r\n========="
              "==============\r\n[L]OGIN\t\tLogin to an existing account.\r\n"
              "[R]EGISTER\tCreate a new account on this BBS."
              "\r\n[A]NONYMOUS\tUse the BBS anonymously.\r\n"
              "[Q]UIT\t\tExit the BBS.")
    while True:
        user.send("--> ", end="")
        command = user.receive().lower()
        if command == "login" or command == "l":
            user.send("USERNAME: ", end="")
            name = user.receive().lower()
            user.send("PASSWORD: ", end="")
            password = user.receive().encode()
            status, last_login = user.database.attempt_login(name, password)
            if status and last_login:
                user.send("Successfully logged in as %s." % name)
                user.send("Last Login: %s." % time.ctime(last_login))
                user.send("Posts since then: %d." %
                          user.database.get_post_count(last_login))
                user.send("You have %d new messages." %
                          user.database.get_pm_count(name))
                break
            else:
                user.send("Invalid login credentials.")
        elif command == "register" or command == "r":
            user.send("USERNAME: ", end="")
            name = user.receive().lower()
            user.send("PASSWORD: ", end="")
            password = user.receive().encode()
            user.send("CONFIRM PASSWORD: ", end="")
            if user.receive().encode() != password:
                user.send("Passwords do not match.")
                continue
            status = user.database.create_user(name, password)
            if status:
                user.send("Account successfully created: %s." % name)
                break
            else:
                user.send("Account already exists, or could not be made.")
        elif command == "anonymous" or command == "a":
            name = "Anonymous"
            status = "coward"
            user.send("Don't make trouble...")
            break
        elif command == "quit" or command == "q":
            name = status = None
            user.close()
            break
        else:
            user.send("Invalid command \"%s\"." % command)
    return (name, status)
