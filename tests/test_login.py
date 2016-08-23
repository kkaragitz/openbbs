import unittest

from openbbs.login import prompt
from tests.dummy_objects import DummyUser


class LoginPromptTest(unittest.TestCase):
    def test_login_user(self):
        dummy_user = DummyUser("login", "a", "a")
        self.assertEqual(prompt(dummy_user), ("a", "user"))

    def test_failed_login(self):
        dummy_user = DummyUser("login", "a", "b", "quit")
        self.assertEqual(prompt(dummy_user), (None, None))

    def test_register_user(self):
        dummy_user = DummyUser("register", "a", "a", "a")
        self.assertEqual(prompt(dummy_user), ("a", "user"))

    def test_failed_registration(self):
        dummy_user = DummyUser("register", "b", "a", "a", "quit")
        self.assertEqual(prompt(dummy_user), (None, None))
        dummy_user.counter = -1
        dummy_user.messages = ("register", "a", "a", "b", "quit")
        self.assertEqual(prompt(dummy_user), (None, None))

    def test_anonymous_login(self):
        dummy_user = DummyUser("anonymous")
        self.assertEqual(prompt(dummy_user), ("Anonymous", "coward"))

    def test_invalid_command(self):
        dummy_user = DummyUser("invalid_command", "quit")
        self.assertEqual(prompt(dummy_user), (None, None))
