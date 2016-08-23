"""Shared dummy objects for unittests."""


class DummyUser(object):
    def __init__(self, *args):
        self.counter = -1
        self.messages = args
        self.database = DummyDatabase()

    def send(self, *args, **kwargs):
        pass

    def receive(self, *args):
        self.counter += 1
        return self.messages[self.counter]

    def close(self):
        pass


class DummyClient(object):
    def __init__(self, *args):
        self.counter = -1
        self.messages = args
        self.database = DummyDatabase()

    def send(self, *args, **kwargs):
        pass

    def recv(self, *args):
        self.counter += 1
        return self.messages[self.counter]

    def close(self):
        pass


class DummyDatabase(object):
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

    def get_post_count(self, time=None):
        return 1

    def get_pm_count(self, *args):
        return 1

    def check_banned(self, name, ip_address):
        if name == "a":
            return "Banned"
