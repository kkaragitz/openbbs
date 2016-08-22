"""Basic command interpereter for the BBS shell."""


class CommandInterpereter(object):
    """Command interpereter to call upon certain functions."""
    def __init__(self, default_function, default_arguments, base_arguments):
        self.base_arguments = base_arguments
        self.commands = {"DEFAULT": (default_function, default_arguments)}

    def add_command(self, aliases, function, arguments):
        """Adds a command and it's function call to the object."""
        if not hasattr(function, "__call__"):
            raise TypeError("\"Function\" argument must be callable.")
        elif not hasattr(arguments, "__iter__"):
            raise TypeError("\"Arguments\" argument must be iterable.")
        elif not hasattr(aliases, "__iter__"):
            raise TypeError("\"Aliases\" argument must be iterable.")
        for name in aliases:
            self.commands[name] = (function, arguments)

    def call_command(self, parameters):
        """Calls the command associated with the given alias."""
        name = parameters[0]
        command, arguments = self.commands.get(name, self.commands["DEFAULT"])
        arguments = self.base_arguments + (parameters,) + arguments
        command(*arguments)

    
        
