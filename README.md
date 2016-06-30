![Asciichan](https://raw.github.com/TsarFox/asciichan/master/Asciichan_Logo.png "Asciichan")
=====
## Server software programmed and maintained by [Jakob.](http://tsar-fox.com/)
Asciichan is a simple BBS server written in Python. It is designed to work on both Python2 and Python3.

Asciichan is free software, licensed under the GNU Affero General Public License.

=============
Main Features
=============

* Users have the option of making an account, or using the BBS anonymously.
* A private message system is available for registered users.
* Moderation is easy, sysops can easily delete posts and ban user accounts.
* Ability to run as a daemon.

============
Installation
============

Currently, the most reliable way to install the Asciichan server is through Pip.

    # It is recommended that you use the latest version of pip and setuptools when installing Asciichan.
    $ pip install --upgrade pip setuptools

    $ pip install --upgrade asciichan

========
Tutorial
========

The server can be invoked with the following.

    $ asciichan-server

However, running it like that is kind of pointless. The server can run as a background process if invoked with the "-b" or "--daemonize" arguments.

    $ asciichan-server --daemonize

Regardless of how it is run, the server will attempt to run according to a config.ini file in the current working directory. If the configuration file is located somewhere else, that should be specified with the "-c" or "--config" parameter.

    $ asciichan-server --daemonize -c /home/user/config.ini

=============
Configuration
=============

The "config.ini" file allows for aspects of the server to be changed.

* name - Change the name that the server will identify as.
* motd - Supply a message to be sent to newly-connected clients.
* rules - A list of rules to be shown to users who run the "rules" command.
* banned - The message that is shown to banned users who attempt to login.
* quit - Message shown to users when they disconnect from the BBS.

* host - The IP that Asciichan will bind to. "dynamic" will attempt to find your machine's IP in the network and bind to that.
* port - The port that the BBS server should bind to.
* backlog - How many connections Asciichan should accept at any one time.
* database - The database file that Asciichan should read and write from.
* logfile - Specify a logfile to write to. If left blank, log messages will be written to stdout.
* boards - Boards on this BBS, separated by comma. A description of the board is specified by adding a colon (:) and the description after the board name.
* operators - List of usernames to be OP'd automatically, separated by comma.

====
TODO
====
- [TODO](/TODO.md)