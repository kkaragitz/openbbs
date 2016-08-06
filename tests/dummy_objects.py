"""Shared dummy objects for unittests."""


class DummyClient(object):
    """Dummy client to test sessions."""
    def __init__(self, *args):
        self.counter = -1
        self.messages = args

    def send(self, *args, **kwargs):
        pass

    def recv(self, *args):
        self.counter += 1
        return self.messages[self.counter]

    def close(self):
        pass


class DummyDatabase(object):
    """Dummy client to test sessions."""
    def close(self):
        pass

    def create_user(self, name, password):
        status = "user" if name == "a" else None
        return status

    def attempt_login(self, name, password):
        if name == "a" and password.decode() == "a":
            status = "user"
        else:
            status = None
        return (status, 1)

    def get_post_count(self, **kwargs):
        return 1

    def get_pm_count(self, *args):
        return 1
