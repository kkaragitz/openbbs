#!/usr/bin/python

import unittest

from tests.dummy_objects import DummyClient

from asciichan.login import prompt
from asciichan.shell import (box_boards, box_posts, box_thread)


def send(*args, **kwargs):
    """Dummy send function."""
    pass


def receive(*args):
    """Dummy receive function."""
    return "quit"


class FormattersTest(unittest.TestCase):
    def test_box_items(self):
        self.assertTrue(box_boards(["board:description"]))
        self.assertTrue(box_posts([[1, 1.0, "a", "a", "a"]]))
        self.assertTrue(box_thread([[1, 1.0, "a", "a", "a"]]))


class LoginTest(unittest.TestCase):
    def test_login_prompt(self):
        self.assertEqual(prompt(send, receive, DummyClient(), None),
                         (None, None))
