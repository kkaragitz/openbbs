#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from openbbs import __version__


def long_description():
    with open("README.md") as description:
        return description.read()


setup(
    name="OpenBBS",
    license="AGPLv3+",
    version=__version__,
    author="Jakob Tsar-Fox",
    author_email="jakob@memeware.net",
    maintainer="Jakob Tsar-Fox",
    maintainer_email="jakob@memeware.net",
    url="http://tsar-fox.com/projects/openbbs",
    description="Simple BBS server written in Python",
    long_description=long_description(),
    download_url="https://github.com/TsarFox/openbbs",
    packages=["openbbs"],
    include_package_data=True,
    install_requires=["python-daemon>=2.1.1"],
    extras_require={},
    tests_require=["tox"],
    entry_points={"console_scripts": ["openbbs-server = openbbs.cli:main"]},
    keywords="bbs telnet server",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications :: BBS",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: System :: Networking",
        "Topic :: Terminals :: Telnet"
    ]
)
