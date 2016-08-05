import unittest

from tests.dummy_objects import (DummyClient, DummyDatabase, dummy_config)

from asciichan.session import (curry_io, handle)


class IOTest(unittest.TestCase):
    def test_curry_io(self):
        client = DummyClient(b"a")
        database = DummyDatabase()
        send, receive = curry_io(client, database, "")
        self.assertTrue(receive())


class ClientHandler(unittest.TestCase):
    def setUp(self):
        self.client = DummyClient(b"quit")
        self.config_get = dummy_config

    def test_handler(self):
        self.assertFalse(handle(self.client, "0.0.0.0", self.config_get))
