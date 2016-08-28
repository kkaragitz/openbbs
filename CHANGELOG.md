Change Log
==========
This document records all notable changes to the OpenBBS codebase.
This project uses the semantic versioning scheme.


**Version 0.5.0**
-----------------
* Added Ascii character 27 to the filter list.
* Implemented a formatter for the private messaging system inbox.
* Read messages will now be automatically deleted when they reach a certain pre-configured age.
* Control character filtering is now much more subtle, and doesn't say when it happens.
* Filtering is now used everywhere a user can provide text input.
* Added a "more" option to read more of a private message, with an accompanying formatter.
* **_DROPPED OFFICIAL SUPPORT FOR PYPY_** as it has serious consistency issues with hashing. Vanilla Python is actually faster when it comes to hashing anyway.


**Version 0.4.0**
-----------------
* Implemented countermeasures for control character injection.
* Fixed thread post formatting.
* Implemented a means of changing the number of hash iterations used and salt length via the configuration file.


**Version 0.3.0**
-----------------
* Changed name of project to "OpenBBS."
* Fixed textwrapping bug.
* Fixed issue with thread creation and hangup.
* Added command shortcuts for the login and shell sessions.


**Version 0.2.0**
-----------------
* Implemented a means of banning IP's from the interface.
* Fixed config.ini parsing on Python2.
* Implemented proper hash salting.
* **_DROPPED OFFICIAL SUPPORT FOR PYTHON VERSIONS 2.6, 3.2 AND 3.3_**


**Version 0.1.1**
---------------
* Replaced newlines with EOL characters to better support clients running Windows.
* Removed private messaging feature for Anonymous users.
* Fixed issue where a client sending "^C" would cause the session to hang.


**Version 0.1**
---------------
* Initial development snapshot.
