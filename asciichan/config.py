"""Version-independent interface to the configparser module."""

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def curry_configuration(path):
    """Returns a function to get a value from the configuration if it 
    exists, otherwise returning a default value.
    """
    config = configparser.ConfigParser()
    config.read(path)

    def config_get(section, option, default=None):
        """Gets a value from the current configuration file if it 
        exists, otherwise returns the given default value.
        """
        if section in config and option in config[section]:
            result = config.get(section, option)
        else:
            result = default
        return result

    return config_get
