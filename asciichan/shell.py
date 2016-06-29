"""Login prompt and shell session to handle client-server interactions."""

import logging
import textwrap
import time

from asciichan import __version__


def box_boards(boards):
    """Text formatter for the BBS's board listiing."""
    string = "=" * 80 + "\n" + "|" + 32 * " " + "BOARD LISTING" + 33 * " "
    string += "|\n" + "=" * 80 + "\n"
    for title, description in [board.split(":") for board in boards]:
        string += "| %-19s|%56s |\n" % (title, description) + "=" * 80 + "\n"
    return string


def box_posts(posts):
    """Text formatter for a listing of threads in one of the BBS's boards."""
    string = "=" * 80 + "\n" + "|" + 32 * " " + "THREAD LISTING" + 32 * " "
    string += "|\n" + "=" * 80 + "\n"
    for post_id, pub_time, poster, subject, body in posts:
        printable_time = time.strftime("%m/%d/%y %H:%M:%S",
                                       time.localtime(pub_time))
        string += "| #%-6d|%.17s| %-19s| %-29.29s|" % (post_id, printable_time,
                                                       poster, subject.strip())
        string += "\n" + "=" * 80 + "\n"
    return string


def box_thread(posts):
    """Returns a table-formatted version of the thread at hand."""
    title = posts[0][3]
    string = "=" * 80 + "\n" + "|" + ((78 - len(title)) // 2) * " " + title
    string += ((78 - len(title)) // 2) * " " + "|\n" + "=" * 80 + "\n"
    for post in posts:
        string += "| #%-9d | %-26s posted on %-26s |\n" % (post[0],
                                                           post[2],
                                                           time.ctime(post[1]))
        string += "=" * 80 + "\n"
        for line in textwrap.wrap(post[4], width=76):
            string += "| %-76s |\n" % line
        string += "=" * 80 + "\n"
    return string


def shell(send, receive, name, status, database, config):
    """Handles basic commands from the currently connected client."""
    boards = config.get("server", "boards").split(",")
    current_board = "main"
    current_thread = None
    send(box_boards(boards))
    send("Enter \"HELP\" to see available commands.\n")
    while True:
        send("%s@%s:%s> " % (name, config.get("messages", "name"),
                             current_board))
        try:
            command = receive().lower().split(" ")
        except UnicodeDecodeError:
            break
        logging.info("%s command received from %s." % (" ".join(command), name))
        if command[0] == "help":
            send("==================\nAVAILABLE COMMANDS\n==================\n"
                 "RULES\t\tPrint the rules of the BBS.\n"
                 "INBOX\t\tGet private messages.\n"
                 "SEND\t\tSend a private message.\n"
                 "BOARD\t\tChange to a specified board.\n"
                 "THREAD\t\tOpen a given thread number.\n"
                 "REFRESH\t\tRefresh the current listing.\n"
                 "POST\t\tMake a post or reply.\n"
                 "INFO\t\tPrint information about this BBS software.\n"
                 "QUIT\t\tExit the BBS.\n")
            if status == "sysop":
                send("DELETE\t\tDelete a post\n"
                     "BAN\t\tBan a username.\n"
                     "UNBAN\t\tUnban a username.\n"
                     "OP\t\tGive a user operator privileges.\n"
                     "DEOP\t\tRevoke operator privileges from a user.\n")
        elif command[0] == "quit":
            break
        elif command[0] == "rules":
            send(config.get("messages", "rules") + "\n")
        elif command[0] == "info":
            send("Asciichan-BBS Server Version %s. Released under the Affero "
                 "General\nPublic License Version 3+.\n" % __version__)
        elif command[0] == "board":
            if len(command) > 1:
                board = command[1]
            else:
                send("BOARD: ")
                board = receive().lower()
            if board in (board.split(":")[0].lower() for board in boards):
                current_board = board
                send(box_posts(database.get_posts(current_board)))
                send("Board successfully changed to \"%s\".\n" % board)
            elif board == "main" or board == "":
                current_board = "main"
                send(box_boards(boards))
                send("Board successfully changed to Main.\n")
            else:
                send("Board \"%s\" does not exist on this BBS.\n" % board)
        elif command[0] == "thread":
            if current_board == "main":
                send("There are no threads here.\n")
            elif len(command) > 1:
                current_thread = command[1]
            else:
                send("Leave empty to return to the thread listing.\nTHREAD "
                     "NUMBER: ")
                current_thread = receive()
            if current_thread == "":
                send(box_posts(database.get_posts(current_board)))
                current_thread = None
            else:
                send(box_thread(database.get_posts(current_board,
                                                   current_thread)))
            send("Current thread changed to %s.\n" % current_thread)
        elif command[0] == "post":
            if current_board == "main":
                send("You can't post here.\n")
            else:
                if current_thread:
                    send("REPLY: ")
                    body = receive()
                    database.make_post(name, None, body, current_board,
                                       reply=current_thread)
                    send("Successfully posted.\n")
                else:
                    send("SUBJECT: ")
                    subject = receive()
                    send("BODY: ")
                    body = receive()
                    database.make_post(name, subject, body, current_board)
                    send("Successfully posted.\n")
        elif command[0] == "send":
            if len(command) > 1:
                receiver = command[1]
            else:
                send("RECEIVER: ")
                receiver = receive()
            if len(command) > 2:
                message = command[2]
            else:
                send("MESSAGE: ")
                message = receive()
            if database.send_pm(name, receiver, message):
                send("Message successfully sent.\n")
            else:
                send("User %s does not exist.\n" % receiver)
        elif command[0] == "inbox":
            messages = database.get_pms(name)
            for sender, message, read in messages:
                read_text = "(*NEW*)" if not read else ""
                send("%s Message from %s: \"%s\"\n" % (read_text, sender,
                                                       message))
        elif command[0] == "refresh":
            if current_thread:
                send(box_thread(database.get_posts(current_board,
                                                   current_thread)))
            elif board == "main":
                send(box_boards(boards))
            else:
                send(box_posts(database.get_posts(current_board)))
        elif command[0] == "delete" and status == "sysop":
            if len(command) > 1:
                target = int(command[1])
            else:
                send("POST ID: ")
                target = receive()
            database.delete_post(target)
            send("Post %d successfully deleted.\n" % target)
        elif command[0] == "ban" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ")
                target = receive()
            if len(command) > 2:
                reason = command[2]
            else:
                send("REASON: ")
                reason = receive()
            if database.ban_user(reason, username=target):
                send("User %s successfully banned.\n" % target)
            else:
                send("User %s does not exist.\n" % target)
        elif command[0] == "unban" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ")
                target = receive()
            database.unban_user(username=target)
            send("User %s successfully unbanned.\n" % target)
        elif command[0] == "op" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ")
                target = receive()
            database.make_op(target)
            send("User %s successfully sysop'd.\n" % target)
        elif command[0] == "deop" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ")
                target = receive()
            database.remove_op(target)
            send("User %s successfully deop'd.\n" % target)
        else:
            try:
                send("Unknown command %s.\n" % " ".join(command))
            except OSError:
                break
    send(config.get("messages", "quit") + "\n")

def login(send, receive, client, database):
    """Provides the connected client with a login prompt, from which they can 
    log into an existing account, create a new one, or choose to browse 
    anonymously.
    """
    send("=" * 23 + "\nPLEASE SELECT AN OPTION\n" + "=" * 23
         + "\nLOGIN\t\tLogin to an existing account.\nREGISTER\tCreate a new "
         "account onthis BBS.\nANONYMOUS\tUse the BBS anonymously.\nQUIT\t\t"
         "Exit the BBS.\n")
    while True:
        send("--> ")
        try:
            command = receive().lower()
        except (UnicodeDecodeError, AttributeError):
            name = status = None
            break
        if command == "login":
            send("USERNAME: ")
            name = receive()
            send("PASSWORD: ")
            password = receive().encode()
            status, last_login = database.attempt_login(name, password)
            if status and last_login:
                send("Successfully logged in as %s.\nLast Login: %s.\nPosts "
                     "since then: %d.\nYou have %d new messages.\n" %
                     (name, time.ctime(last_login),
                      database.get_post_count(last_login=last_login),
                      database.get_pm_count(name)))
                break
            else:
                send("Invalid login credentials.\n")
        elif command == "register":
            send("USERNAME: ")
            name = receive()
            status = "sysop" if name in database.operators else "user"
            send("PASSWORD: ")
            password = receive()
            send("CONFIRM PASSWORD: ")
            if receive() != password:
                send("Passwords do not match.\n")
                continue
            elif database.create_user(name, password.encode()):
                send("Account successfully created: %s.\n" % name)
                break
            else:
                send("Account already exists.\n")
        elif command == "anonymous":
            name = "Anonymous"
            send("Don't make trouble...\n")
            status = "coward"
            break
        elif command == "quit":
            name = status = None
            break
        else:
            send("Invalid command \"%s\".\n" % command)
    return name, status
