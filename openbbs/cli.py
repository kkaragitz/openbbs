"""Argument definitions for invokation from the command-line."""

import argparse

from openbbs import (__doc__, __version__)


class CustomHelp(argparse.HelpFormatter):
    """Small modifications argparse's default HelpFormatter."""

    def _fill_text(self, text, width, indent):
        return "".join(indent + line
                       for line in text.splitlines(keepends=True))

    def _split_lines(self, text, width):
        return text.splitlines()

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "Usage: "
        return super(CustomHelp, self).add_usage(usage, actions, groups,
                                                 prefix)


parser = argparse.ArgumentParser(
    add_help=False,
    formatter_class=CustomHelp,
    usage="%(prog)s [OPTIONS]",
    description=__doc__
)


docs = parser.add_argument_group("Documentation")
docs.add_argument(
    "-h",
    "--help",
    action="help",
    help="Display this help page and exit."
)
docs.add_argument(
    "-v",
    "--version",
    action="version",
    version="OpenBBS Server, Version %s." % __version__,
    help="Display the currently installed version and exit."
)


server_opts = parser.add_argument_group("Server Options")
server_opts.add_argument(
    "-b",
    "--daemonize",
    action="store_true",
    help="Run the server as a UNIX daemon. (Background Process)\n\n"
)
server_opts.add_argument(
    "-c",
    "--config",
    metavar="XX",
    default="./config.ini",
    help="Specify the path of the config.ini file that the OpenBBS\nserver "
    "should read from."
)
