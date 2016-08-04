![Asciichan](https://raw.github.com/TsarFox/asciichan/master/Asciichan_Logo.png "Asciichan")
=========
## Server software programmed and maintained by [Jakob.](http://tsar-fox.com/)
Asciichan is a simple text-based BBS server written in Python, designed to work with both major versions of Python. Its goal is to be easily accessible to anyone with Netcat or a Telnet client.

Asciichan is free software, licensed under the GNU Affero General Public License.

[![Build Status](https://travis-ci.org/TsarFox/asciichan.svg?branch=master)](https://travis-ci.org/TsarFox/asciichan)  [![PyPI Downloads](https://img.shields.io/pypi/dm/Asciichan.svg)](https://pypi.python.org/pypi/Asciichan/)  [![License](https://img.shields.io/github/license/tsarfox/asciichan.svg)](https://www.gnu.org/licenses/agpl-3.0.html)


Primary Features
================

* Users can either sign up for an account, or use the BBS anonymously.
* Remote moderation is simple, operators should have little to  no trouble deleting posts and banning users.
* Fully-featured private messaging system for registered users.


Installation
------------

Currently, the most reliable way to install the Asciichan server is through Pip.

    # It is recommended that you use the latest version of pip and setuptools when installing Asciichan.
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade asciichan


Tutorial
--------

The server can be invoked with the following.

    $ asciichan-server

However, running it like that is kind of pointless. The server can run as a background process if invoked with the "-b" or "--daemonize" arguments.

    $ asciichan-server --daemonize

Regardless of how it is run, the server will attempt to run according to a config.ini file in the current working directory. If the configuration file is located somewhere else, that should be specified with the "-c" or "--config" parameter.

    $ asciichan-server --daemonize -c /home/user/config.ini

The easiest way to connect to the server is through telnet, although other tools such as Netcat can also be used.

    $ telnet [ip] [port] # Alternatively, "nc [ip] [port]" if you prefer to use Netcat.
    ...


Configuration
-------------

The "config.ini" file allows for aspects of the server to be changed.

*[messages]*
* name - Change the name that the server will identify as.
* motd - Supply a message to be sent to newly-connected clients.
* rules - A list of rules to be shown to users who run the "rules" command.
* banned - The message that is shown to banned users who attempt to login.
* quit - Message shown to users when they disconnect from the BBS.

*[server]*
* host - The IP that Asciichan will bind to.
* port - The port that the BBS server should bind to.
* backlog - How many connections Asciichan should accept at any one time.
* database - The database file that Asciichan should read and write from.
* logfile - Specify a logfile to write to. If left blank, log messages will be written to stdout.
* boards - Boards on this BBS, separated by comma. A description of the board is specified by adding a colon (:) and the description after the board name.
* operators - List of usernames to be given operator automatically, separated by comma. Changes will take effect when they register or login.


TODO
----
- [TODO](/TODO.md)