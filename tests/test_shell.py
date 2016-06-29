#!/usr/bin/python

import unittest

import tests.dummy_objects

import asciichan.shell


def send(*args):
    """Dummy send function."""
    pass


def receive(*args):
    """Dummy receive function."""
    return "quit"


class FormattersTest(unittest.TestCase):
    def test_box_items(self):
        self.assertTrue(asciichan.shell.box_boards(["board:description"]))
        self.assertTrue(asciichan.shell.box_posts([[1, 1.0, "a", "a", "a"]]))
        self.assertTrue(asciichan.shell.box_thread([[1, 1.0, "a", "a", "a"]]))


class LoginTest(unittest.TestCase):
    def test_login_prompt(self):
        self.assertEqual(asciichan.shell.login(
            send,
            receive,
            tests.dummy_objects.DummyClient(),
            None
        ), (None, None))
