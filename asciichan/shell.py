"""Interactive shell for communication between the client and BBS."""

import logging
import textwrap
import time

from asciichan import __version__


def box_boards(boards):
    """Text formatter for the board listing."""
    string = "+=============================================================="\
             "================+\r\n|                                BOARD LIS"\
             "TING                                 |\r\n+===================="\
             "==========================================================+\r\n"
    for title, description in [board.split(":") for board in boards]:
        string += "| %-18s | %55s |\r\n+====================================="\
                  "=========================================+\r\n" % \
                  (title, description)
    return string


def box_posts(posts):
    """Text formatter for a listing of threads in a board."""
    string = "+=============================================================="\
             "================+\r\n|                                THREAD LI"\
             "STING                                |\r\n+===================="\
             "==========================================================+\r\n"
    for post_id, pub_time, poster, subject, body in posts:
        printable_time = time.strftime("%m/%d/%y %H:%M:%S",
                                       time.localtime(pub_time))
        string += "| #%-6d|%.17s| %-19s| %-29.29s|\r\n+======================"\
        "========================================================+" % \
        (post_id, printable_time, poster, subject.strip())
    return string


def box_thread(posts):
    """Returns a table-formatted version of the thread being viewed."""
    title = posts[0][3]
    string = "+=============================================================="\
             "================+\r\n|" + ((78 - len(title)) // 2) * " " + title\
             + ((78 - len(title)) // 2) * " " + "|\r\n+======================"\
             "========================================================+\r\n"
    for post in posts:
        post_time = time.ctime(post[1])
        string += "| #%-9d | %-26s posted on %-26s |\r\n+===================="\
                  "=========================================================="\
                  "+\r\n" % (post[0], post[2], post_time)
        for line in textwrap.wrap(post[4], width=76):
            string += "| %-76s |\r\n" % line
        string += "+========================================================="\
                  "=====================+\r\n"
    return string


def shell(send, receive, name, status, database, config):
    """Handles basic commands from the currently connected client."""
    boards = config.get("server", "boards", fallback="test:test").split(",")
    current_board = "main"
    current_thread = None
    send(box_boards(boards))
    send("Enter \"HELP\" to see available commands.")
    while True:
        send("[%s@%s %s]$ " % (name, config.get("messages", "name",
                                                fallback="Asciichan-BBS"),
                               current_board), end="")
        try:
            command = receive().lower().split(" ")
        except UnicodeDecodeError:
            break
        logging.info("\"%s\" command received from %s.", " ".join(command),
                     name)
        if command[0] == "help":
            send("==================\r\nAVAILABLE COMMANDS\r\n================"
                 "==\r\nRULES\t\tPrint the rules of the BBS.\r\n"
                 "BOARD\t\tChange to a specified board.\r\n"
                 "THREAD\t\tOpen a given thread number.\r\n"
                 "REFRESH\t\tRefresh the current listing.\r\n"
                 "POST\t\tMake a post or reply.\r\n"
                 "INFO\t\tPrint information about this BBS software.\r\n"
                 "QUIT\t\tExit the BBS.")
            if status != "coward":
                send("INBOX\t\tGet private messages.\r\n"
                     "SEND\t\tSend a private message.")
            if status == "sysop":
                send("DELETE\t\tDelete a post\r\n"
                     "BAN\t\tBan a username.\r\n"
                     "UNBAN\t\tUnban a username.\r\n"
                     "OP\t\tGive a user operator privileges.\r\n"
                     "DEOP\t\tRevoke operator privileges from a user.")
        elif command[0] == "quit":
            break
        elif command[0] == "rules":
            send(config.get("messages", "rules", fallback=""))
        elif command[0] == "info":
            send("Asciichan-BBS Server Version %s. Released under the Affero "
                 "General Public\r\nLicense Version 3+." % __version__)
        elif command[0] == "board":
            if len(command) > 1:
                board = command[1]
            else:
                send("BOARD: ", end="")
                board = receive().lower()
            if board in (board.split(":")[0].lower() for board in boards):
                current_board = board
                send(box_posts(database.get_posts(current_board)))
                send("Board successfully changed to \"%s\"." % board)
            elif board == "main" or board == "":
                current_board = "main"
                send(box_boards(boards))
                send("Board successfully changed to Main.")
            else:
                send("Board \"%s\" does not exist on this BBS." % board)
        elif command[0] == "thread":
            if current_board == "main":
                send("There are no threads here.\r\n")
            elif len(command) > 1:
                current_thread = command[1]
            else:
                send("Leave empty to return to the thread listing.\r\nTHREAD "
                     "NUMBER: ", end="")
                current_thread = receive()
            if current_thread == "":
                send(box_posts(database.get_posts(current_board)))
                send("Successfully returned to the %s home." % current_board)
                current_thread = None
            else:
                posts = database.get_posts(current_board, current_thread)
                if posts:
                    send(box_thread(posts))
                    send("Current thread changed to %s." % current_thread)
                else:
                    send("Thread %s does not exist." % current_thread)
                    current_thread = None
        elif command[0] == "post":
            if current_board == "main":
                send("You can't post here.")
            else:
                if current_thread:
                    send("REPLY: ", end="")
                    body = receive()
                    database.make_post(name, None, body, current_board,
                                       reply=current_thread)
                    send("Successfully posted.")
                else:
                    send("SUBJECT: ", end="")
                    subject = receive()
                    send("BODY: ", end="")
                    body = receive()
                    database.make_post(name, subject, body, current_board)
                    send("Successfully posted.")
        elif command[0] == "refresh":
            if current_thread:
                send(box_thread(database.get_posts(current_board,
                                                   current_thread)))
            elif current_board == "main":
                send(box_boards(boards))
            else:
                send(box_posts(database.get_posts(current_board)))
        elif command[0] == "send" and status != "coward":
            if len(command) > 1:
                receiver = command[1].lower()
            else:
                send("RECEIVER: ", end="")
                receiver = receive().lower()
            if len(command) > 2:
                message = command[2]
            else:
                send("MESSAGE: ", end="")
                message = receive()
            if database.send_pm(name, receiver, message):
                send("Message successfully sent.")
            else:
                send("User %s does not exist." % receiver)
        elif command[0] == "inbox" and status != "coward":
            messages = database.get_pms(name)
            for sender, message, timesent, read in messages:
                read_text = "(*NEW*) " if not read else ""
                send("%s[%s] Message from %s: \"%s\"" % (read_text,
                                                         time.ctime(timesent),
                                                         sender, message))
        elif command[0] == "delete" and status == "sysop":
            if len(command) > 1:
                target = int(command[1])
            else:
                send("POST ID: ", end="")
                target = receive()
            database.delete_post(target)
            send("Post %d successfully deleted." % target)
        elif command[0] == "ban" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ", end="")
                target = receive()
            if len(command) > 2:
                reason = command[2]
            else:
                send("REASON: ", end="")
                reason = receive()
            if database.ban_user(reason, username=target):
                send("User %s successfully banned." % target)
            else:
                send("User %s does not exist." % target)
        elif command[0] == "unban" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ", end="")
                target = receive()
            database.unban_user(username=target)
            send("User %s successfully unbanned." % target)
        elif command[0] == "op" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ", end="")
                target = receive()
            database.make_op(target)
            send("User %s successfully sysop'd." % target)
        elif command[0] == "deop" and status == "sysop":
            if len(command) > 1:
                target = command[1]
            else:
                send("USER: ", end="")
                target = receive()
            database.remove_op(target)
            send("User %s successfully deop'd." % target)
        else:
            try:
                send("Unknown command %s." % " ".join(command))
            except OSError:
                break
    send(config.get("messages", "quit", fallback="Goodbye!"))
