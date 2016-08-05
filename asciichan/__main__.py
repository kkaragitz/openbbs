#!/usr/bin/env python

"""Command-line entry point to the Asciichan server."""

import sys

from asciichan.core import main


if __name__ == "__main__":
    sys.exit(main())
