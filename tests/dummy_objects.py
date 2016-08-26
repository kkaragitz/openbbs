"""Shared dummy objects for unittests."""


class DummyUser(object):
    def __init__(self, *args):
        self.counter = -1
        self.messages = args
        self.database = DummyDatabase()
        self.name = "DummyUser"
        self.status = "sysop"
        self.current_board = "main"
        self.current_thread = None
        self.last_message = ""

    def send(self, message, end="\r\n"):
        self.last_message = message + end

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

    def get_posts(self, board, thread=None):
        if thread == "2":
            posts = None
        else:
            posts = ((1, 1, "a", "a", "a"),)
        return posts

    def make_post(self, *args, **kwargs):
        pass

    def send_pm(self, sender, receiver, message):
        if receiver == "meme2":
            sent = False
        else:
            sent = True
        return sent

    def delete_post(self, target):
        pass

    def ban_user(self, reason, username=None):
        pass

    def unban_user(self, username):
        pass

    def get_pms(self, name):
        if name == "DummyUserEmpty":
            messages = ()
        else:
            messages = ((1, "a", "a", 1, False),)
        return messages

    def get_specific_pm(self, name, message_id):
        if name == "DummyUserEmpty":
            message = ()
        else:
            message = ("a", "a")
        return message

    def make_op(self, target):
        pass

    def remove_op(self, target):
        pass
