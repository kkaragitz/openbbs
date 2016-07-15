"""Entry point to the Asciichan server process."""

import sys
import argparse

import asciichan.core


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


def parse_arguments():
    """Parse command-line arguments and return the namespace."""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=CustomHelp,
        usage="%(prog)s [path/to/config.ini] [OPTIONS]",
        description=asciichan.__doc__)
    docs = parser.add_argument_group("Documentation")
    docs.add_argument("-h",
                      "--help",
                      action="help",
                      help="Display this help page and exit.")
    docs.add_argument("-v",
                      "--version",
                      action="version",
                      version="Asciichan Server Version %s." %
                      asciichan.__version__,
                      help="Display the currently installed version and exit.")
    server_opts = parser.add_argument_group("Server Options")
    server_opts.add_argument("-b",
                             "--daemonize",
                             action="store_true",
                             help="Run the server as a UNIX daemon. "
                             "(Background Process)")
    server_opts.add_argument("-c",
                             "--config",
                             metavar="XX",
                             default="./config.ini",
                             help="Specify the path of the config.ini file "
                             "that the Asciichan\nserver should read from.")
    return parser.parse_args()


def main():
    """Command-line entry point to Asciichan."""
    sys.exit(asciichan.core.main(parse_arguments()))
