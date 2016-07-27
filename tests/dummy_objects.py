"""Shared dummy objects for unittests."""

class DummyClient(object):
    """Dummy client to test sessions."""
    def send(self, *args):
        pass

    def recv(self, *args):
        return b"quit"

    def close(self):
        pass


class DummyDatabase(object):
    """Dummy client to test sessions."""
    def close(self):
        pass


class DummyConfig(object):
    """Dummy config to test sessions."""
    def get(self, *args, **kwargs):
        if args[1] == "database":
            return "database.db"
        elif args[1] == "operators":
            return ""
        elif args[1] == "motd":
            return "This is a test MOTD."
