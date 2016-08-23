"""Basic command interpreter for use in the BBS shell."""


class CommandInterpreter(object):
    """Command interpreter class, which maintains a table of command
    aliases and their corresponding functions/parameters.
    """
    def __init__(self, default_function, default_arguments, base_arguments):
        self.base_arguments = base_arguments
        self.commands = {"DEFAULT": (default_function, default_arguments)}

    def add(self, aliases, function, arguments):
        """Appends the given function and its arguments to the
        interpreter's command table under all of the given aliases.
        """
        if not hasattr(aliases, "__iter__"):
            raise TypeError("\"Aliases\" argument must be iterable.")
        elif not hasattr(function, "__call__"):
            raise TypeError("\"Function\" argument must be callable.")
        elif not hasattr(arguments, "__iter__"):
            raise TypeError("\"Arguments\" argument must be iterable.")
        for name in aliases:
            self.commands[name] = (function, arguments)

    # Return value is typically unused, but kept for testing purposes.
    def call(self, command):
        """Finds the function and arguments associated with the given
        alias, calls the function and returns its value.
        """
        name = command[0]
        function, arguments = self.commands.get(name, self.commands["DEFAULT"])
        arguments = self.base_arguments + (command,) + arguments
        return function(*arguments)
