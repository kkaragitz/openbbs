#!/usr/bin/env python

"""Command-line entry point to the OpenBBS server."""

import sys

from openbbs.core import main


if __name__ == "__main__":
    sys.exit(main())
