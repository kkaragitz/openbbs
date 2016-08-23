import unittest

from openbbs.config import load_config
from openbbs.session import UserSession, handle
from tests.dummy_objects import (DummyClient, DummyDatabase)


class UserEncapsulationTest(unittest.TestCase):
    def test_basic_user(self):
        client = DummyClient(b"a")
        database = DummyDatabase()
        user = UserSession(client, database, "")
        self.assertTrue(user.receive())
        with self.assertRaises(SystemExit):
            user.close()


class ClientHandler(unittest.TestCase):
    def test_handler(self):
        config = load_config("./inexistent.ini")
        client = DummyClient(b"quit")
        with self.assertRaises(SystemExit):
            handle(client, "", config)
