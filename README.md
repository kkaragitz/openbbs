**THIS REPOSITORY IS NO LONGER ACTIVELY MAINTAINED.**

![OpenBBS](https://raw.github.com/TsarFox/openbbs/master/OpenBBS_Logo.png "OpenBBS")
=========
## Server software programmed and maintained by [Jakob.](http://tsar-fox.com/)
OpenBBS is a simple text-based BBS server written in Python. Its goal is to be easily accessible to anyone with Netcat or a Telnet client, and functional on both major versions of Python.

OpenBBS is free software, licensed under the GNU Affero General Public License.

[![Build Status](https://travis-ci.org/TsarFox/openbbs.svg?branch=master)](https://travis-ci.org/TsarFox/openbbs)  [![PyPI Downloads](https://img.shields.io/pypi/dm/OpenBBS.svg)](https://pypi.python.org/pypi/OpenBBS/)  [![License](https://img.shields.io/github/license/tsarfox/openbbs.svg)](https://www.gnu.org/licenses/agpl-3.0.html)


Primary Features
================

* In addition to support for registered accounts, users are also able to browse the BBS anonymously.
* Remote moderation is simple, operators should have little to no trouble deleting posts and banning users.
* Registered users are able to use a fully-featured private messaging system.


Installation
------------

Currently, the most reliable way to install the OpenBBS server is through Pip.

    # It is recommended that you use the latest version of pip and setuptools when installing OpenBBS.
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade openbbs


Tutorial
--------

The server can be invoked with the following.

    $ openbbs-server

However, running it like that is kind of pointless. The server can run as a background process if invoked with the "-b" or "--daemonize" arguments.

    $ openbbs-server --daemonize

Regardless of how it is run, the server will attempt to run according to a config.ini file in the current working directory. If the configuration file is located somewhere else, that should be specified with the "-c" or "--config" parameter.

    $ openbbs-server --daemonize -c /home/user/config.ini

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
* host - The IP that OpenBBS will bind to.
* port - The port that the BBS server should bind to.
* backlog - How many connections OpenBBS should accept at any one time.
* database - The database file that OpenBBS should read and write from. ":memory:" unfortunately does not work at this time, as no database transactions will be committed.
* logfile - Specify a logfile to write to. If left blank, log messages will be written to stdout.
* boards - Boards on this BBS, separated by comma. A description of the board is specified by adding a colon (:) and the description after the board name.
* operators - List of usernames to be given operator automatically, separated by comma. Changes will take effect when they register or login.

*[server]*
* hash_iterations - The number of iterations to be used in PBKDF2 password hashing. More will bring better security, but having it at too high of a value will make login and registration take a very long time. This should be changed ahead of time, as changing it for an existing database will make it impossible for users to log in.
* salt_length - The length (in bytes) of the cryptographic salt to be generated for each user. More is better, but going overkill here isn't going to be particularly helpful. Unlike hash_iterations, this can be changed for an existing database, but users who registered before the change will still have a salt length of the previous value.

*[client]*
* max_message_age - The period of time (in seconds) the BBS should wait before deleting read messages. Setting this to 0 will disable the automatic message deletion feature altogether.


TODO
----
- [TODO](/TODO.md)
