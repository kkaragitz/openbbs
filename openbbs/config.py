"""Version-independent wrapper around the configparser module."""

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DEFAULTS = {
    "name": "OpenBBS",
    "motd": "Welcome to OpenBBS!",
    "rules": "",
    "banned": "You have been banned!",
    "quit": "Thank you for connecting!",
    "host": "",
    "port": 1337,
    "backlog": 5,
    "database": "./database.db",
    "logfile": None,
    "boards": "Random:Posts without a home.,Technology:Install Gentoo.",
    "operators": ""
}


def load_config(path):
    """Version-agnostic wrapper around the configparser module. Returns a
    "squashed" dictionary containing all options.
    """
    config = DEFAULTS
    config_file = configparser.ConfigParser()
    config_file.read(path)

    for section in config_file.sections():
        for option in config_file.options(section):
            config[option] = config_file.get(section, option)

    return config
