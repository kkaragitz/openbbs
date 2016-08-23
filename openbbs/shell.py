"""Interactive shell for communication between the client and BBS."""

import logging
import textwrap
import time

from openbbs import __version__
from openbbs.command import CommandInterpreter


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


def handle_bogus_input(user, parameters):
    """[Document me!]"""
    user.send("Unknown command: \"%s\"" % parameters[0])


def send_help_text(user, _):
    """Sends the user a list of available commands."""
    user.send("==================\r\nAVAILABLE COMMANDS\r\n=================="
              "\r\n[R]ULES\t\tPrint the rules of the BBS.\r\n"
              "[B]OARD\t\tChange to a specified board.\r\n"
              "[T]HREAD\t\tOpen a given thread number.\r\n"
              "[RE]FRESH\t\tRefresh the current listing.\r\n"
              "[P]OST\t\tMake a post or reply.\r\n"
              "[IN]FO\t\tPrint information about this BBS software.\r\n"
              "[Q]UIT\t\tExit the BBS.")
    if user.status != "coward":
        user.send("[I]NBOX\t\tGet private messages.\r\n"
                  "[S]END\t\tSend a private message.")
    if user.status == "sysop":
        user.send("[D]ELETE\t\tDelete a post\r\n"
                  "[BA]N\t\tBan a username.\r\n"
                  "[U]NBAN\t\tUnban a username.\r\n"
                  "[O]P\t\tGive a user operator privileges.\r\n"
                  "[DE]OP\t\tRevoke operator privileges from a user.")


def send_rules(user, _, config):
    """Sends the user the configuration-defined rules."""
    user.send(config.get("rules", ""))


def send_server_info(user, _):
    """Sends the user information about the server software."""
    user.send("OpenBBS Server Version %s.\r\nReleased under the GNU Affero "
              "General Public License Version 3+." % __version__)


def change_board(user, parameters, boards):
    """Changes the user's current board, if valid."""
    if len(parameters) > 1:
        board = parameters[1]
    else:
        user.send("Leave empty to return to the overboard.\r\nBOARD: ", end="")
        board = user.receive().lower()

    if board in (board.split(":")[0].lower() for board in boards):
        user.send(box_posts(user.database.get_posts(board)))
        user.send("Board successfully changed to \"%s\"." % board)
        user.current_board = board.lower()
    elif board == "":
        user.current_board = "main"
        user.send(box_boards(boards))
        user.send("Successfully returned to the overboard.")
    else:
        user.send("Board \"%s\" does not exist on this BBS." % board)


def change_thread(user, parameters):
    """Changes the user's current thread, if valid."""
    if user.current_board == "main":
        user.send("There are no threads here.")
    elif len(parameters) > 1:
        user.current_thread = parameters[1]
    else:
        user.send("Leave empty to return to the thread listing.\r\nTHREAD "
                  "NUMBER: ", end="")
        thread = user.receive()
        if thread == "":
            user.current_thread = None
            user.send(box_posts(user.database.get_posts(user.current_board)))
            user.send("Successfully returned to the %s home." % current_board)
        else:
            posts = user.database.get_posts(user.current_board, thread)
            if posts:
                user.current_thread = thread
                user.send(box_thread(posts))
                user.send("Current thread changed to %s." % thread)
            else:
                current_thread = None
                user.send("Thread %s does not exist." % thread)


def get_inbox(user, parameters):
    """Sends the user their inbox, provided they are not anonymous."""
    if user.status != "coward":
        messages = user.database.get_pms(user.name)
        for sender, message, timesent, read in messages:
            read_text = "(*NEW*) " if not read else ""
            user.send("%s[%s] Message from %s: \"%s\"" %
                      (read_text, time.ctime(timesent), sender, message))
        if len(messages) == 0:
            user.send("Your inbox is empty.")
    else:
        user.send("You can't do that!")


def make_post(user, _):
    """Makes a post in the database, if possible."""
    if user.current_board == "main":
        user.send("You can't post on the overboard.")
    else:
        if user.current_thread:
            user.send("REPLY: ", end="")
            body = user.receive()
            user.database.make_post(user.name, None, body, user.current_board,
                                    reply=user.current_thread)
            user.send("Successfully posted.")
        else:
            user.send("SUBJECT: ", end="")
            subject = user.receive()
            user.send("BODY: ", end="")
            body = user.receive()
            database.make_post(user.name, subject, body, user.current_board)
            user.send("Successfully posted.")


def refresh_all(user, _, boards):
    """Gets the latest posts or threads, depending on where the user is
    in the BBS.
    """
    if user.current_thread:
        user.send(box_thread(user.database.get_posts(user.current_board,
                                                     user.current_thread)))
    elif user.current_board == "main":
        user.send(box_boards(boards))
    else:
        user.send(box_posts(user.database.get_posts(user.current_board)))


def send_message(user, parameters):
    """Sends a private message to a user, if possible."""
    if user.status != "coward":
        if len(parameters) > 1:
            receiver = parameters[1].lower()
        else:
            user.send("RECEIVER: ", end="")
            receiver = user.receive().lower()
        if len(parameters) > 2:
            message = command[2]
        else:
            user.send("MESSAGE: ", end="")
            message = user.receive()
        if user.database.send_pm(user.name, receiver, message):
            user.send("Message successfully sent.")
        else:
            user.send("User %s does not exist." % receiver)
    else:
        user.send("You can't do that!")


def delete_post(user, parameters):
    """Deletes a post if the user has that capability."""
    if user.status == "sysop":
        if len(parameters) > 1:
            target = int(parameters[1])
        else:
            user.send("POST ID: ", end="")
            target = user.receive()
        user.database.delete_post(target)
        user.send("Post %d successfully deleted." % target)
    else:
        user.send("You can't do that!")


def ban_user(user, parameters):
    """Bans a user if the user has that capability."""
    if user.status == "sysop":
        if len(parameters) > 1:
            target = parameters[1]
        else:
            user.send("USER: ", end="")
            target = user.receive()
        if len(parameters) > 2:
            reason = command[2]
        else:
            user.send("REASON: ", end="")
            reason = user.receive()
        user.database.ban_user(reason, username=target)
        user.send("User %s successfully banned." % target)
    else:
        user.send("You can't do that!")


def unban_user(user, parameters):
    """Unbans a user if the user has that capability."""
    if user.status == "sysop":
        if len(parameters) > 1:
            target = parameters[1]
        else:
            user.send("USER: ", end="")
            target = user.receive()
        user.database.unban_user(username=target)
        user.send("User %s successfully unbanned." % target)
    else:
        user.send("You can't do that!")


def op_user(user, parameters):
    """Op's a user if the user has that capability."""
    if user.status == "sysop":
        if len(parameters) > 1:
            target = parameters[1]
        else:
            user.send("USER: ", end="")
            target = user.receive()
        user.database.make_op(target)
        user.send("User %s successfully sysop'd." % target)
    else:
        user.send("You can't do that!")


def deop_user(user, parameters):
    """Deop's a user if the user has that capability."""
    if user.status == "sysop":
        if len(parameters) > 1:
            target = parameters[1]
        else:
            user.send("USER: ", end="")
            target = user.receive()
        user.database.remove_op(target)
        user.send("User %s successfully deop'd." % target)
    else:
        user.send("You can't do that!")


def shell(user, config):
    """Handles basic commands from the currently connected client."""
    boards = config.get("boards").split(",")

    command = ["DEFAULT", "NULL"]
    command_interpreter = CommandInterpreter(handle_bogus_input, (), (user,))
    command_interpreter.add(("help", "h"), send_help_text, ())
    command_interpreter.add(("rules", "r"), send_rules, (config,))
    command_interpreter.add(("info", "in"), send_server_info, ())
    command_interpreter.add(("board", "b"), change_board, (boards,))
    command_interpreter.add(("thread", "t"), change_thread, ())
    command_interpreter.add(("inbox", "i"), get_inbox, ())
    command_interpreter.add(("refresh", "re"), refresh_all, (boards,))
    command_interpreter.add(("post", "p"), make_post, ())
    command_interpreter.add(("send", "s"), send_message, ())
    command_interpreter.add(("delete", "d"), delete_post, ())
    command_interpreter.add(("ban", "ba"), ban_user, ())
    command_interpreter.add(("unban", "u"), unban_user, ())
    command_interpreter.add(("op", "o"), op_user, ())
    command_interpreter.add(("deop", "de"), deop_user, ())

    user.send(box_boards(boards))
    user.send("Enter \"[H]ELP\" to see available commands.")

    while True:
        user.send("[%s@%s %s]$ " % (user.name, config.get("name"),
                                    user.current_board), end="")
        command = user.receive().lower().split(" ")
        logging.info("\"%s\" command received from %s.", " ".join(command),
                     user.name)
        if command[0] == "quit" or command[0] == "q":
            break
        else:
            command_interpreter.call(command)

    user.send(config.get("quit"))
