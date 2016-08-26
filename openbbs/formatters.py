"""General text formatters to be used as shell output."""

import textwrap
import time

DISALLOWED_CHARACTERS = (7, 8, 12, 26, 27, 127)


def scrub_input(text):
    """Removes control-character injection from the given text."""
    return text.strip("".join((chr(value) for value in DISALLOWED_CHARACTERS)))


def box_boards(boards):
    """Formats the given boards into a nice-looking listing."""
    string = "+=============================================================" \
             "=================+\r\n|                                BOARD L" \
             "ISTING                                 |\r\n+=================" \
             "=============================================================+" \
             "\r\n"

    for title, description in (board.split(":") for board in boards):
        string += "| %-18s | %55s |\r\n+====================================" \
                  "==========================================+\r\n" % \
                  (scrub_input(title), scrub_input(description))

    return string


def box_posts(posts):
    """Formats a list of threads into a nice-looking listing."""
    string = "+=============================================================" \
             "=================+\r\n|                                THREAD " \
             "LISTING                                |\r\n+=================" \
             "=============================================================+" \
             "\r\n"

    for post_id, pub_time, poster, subject, _ in posts:
        time_text = time.strftime("%m/%d/%y %H:%M:%S",
                                  time.localtime(pub_time))
        string += "| #%-6d| %.17s | %-19s| %-27.27s|\r\n+===================" \
                  "=========================================================" \
                  "==+\r\n" % (post_id, time_text, scrub_input(poster),
                               scrub_input(subject.strip()))

    return string


def box_thread(posts):
    """Formats a list of posts into a nice-looking listing."""
    title = scrub_input(posts[0][3])
    if len(title) % 2 == 1:
        title += " "

    string = "+=============================================================" \
             "=================+\r\n|" + ((78 - len(title)) // 2) * " " \
             + "%.78s" % title + ((78 - len(title)) // 2) * " " + "|\r\n+===" \
             "==============================================================" \
             "=============+\r\n"

    for post_id, post_time, name, _, body in posts:
        body = scrub_input(body)
        string += "| #%-9d | %-26s posted on %-26s |\r\n+===================="\
                  "=========================================================="\
                  "+\r\n" % (post_id, scrub_input(name), time.ctime(post_time))

        for line in textwrap.wrap(body, width=76):
            string += "| %-76s |\r\n" % line
        string += "+========================================================" \
                  "======================+\r\n"

    return string


def box_inbox(messages):
    """Formats a list of private messages into a nice-looking inbox."""
    string = "+=============================================================" \
             "=================+\r\n|                                    INB" \
             "OX                                     |\r\n+=================" \
             "=============================================================+" \
             "\r\n"

    for message_id, sender, message, timesent, read in messages:
        text_time = time.strftime("%m/%d/%y", time.localtime(timesent))
        message = message[:26] + "..." if len(message) >= 29 else message
        message_status = "R" if read else "N"

        string += "| %1s | #%-4s | From %-10s on %-11s | \"%-29s\" |\r\n+===" \
                  "=========================================================" \
                  "==================+\r\n" % (message_status, message_id,
                                               scrub_input(sender), text_time,
                                               scrub_input(message))

    return string


def box_message(message):
    """Format a private message into a box similar to a post's."""
    sender, message = message
    title = "Message from %s" % scrub_input(sender)
    if len(title) % 2 == 1:
        title += " "

    string = "+=============================================================" \
             "=================+\r\n|" + ((78 - len(title)) // 2) * " " \
             + "%.78s" % title + ((78 - len(title)) // 2) * " " + "|\r\n+===" \
             "==============================================================" \
             "=============+\r\n"

    for line in textwrap.wrap(scrub_input(message), width=76):
        string += "| %-76s |\r\n" % line
    string += "+========================================================" \
              "======================+\r\n"

    return string
