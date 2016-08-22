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
    "operators": "",
    "anonymous_enabled": True # Currently unused.
}


# Configparser is a disgusting module, please continue to use a wrapper for it.
def load_config(path):
    """Version-agnostic wrapper around the configparser module. Returns a
    "squashed" dictionary containing all options.
    """
    # Overwriting doesn't necessarily matter, so we don't need to deepcopy.
    config = DEFAULTS
    config_file = configparser.ConfigParser()
    config_file.read(path)

    # config.ini acts as an override for the configuration defaults.
    # Non-idiomatic iteration is for Python2 compatibility.
    for section in config_file.sections():
        for option in config_file.options(section):
            config[option] = config_file.get(section, option)

    return config
