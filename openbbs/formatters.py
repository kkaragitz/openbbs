"""General text formatters for the shell."""

import textwrap
import time


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
