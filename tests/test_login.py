#!/usr/bin/env python

import unittest

from tests.dummy_objects import (DummyClient, DummyDatabase)

from asciichan.login import prompt


class LoginPromptTest(unittest.TestCase):
    def test_login_user(self):
        client = DummyClient("login", "a", "a")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         ("a", "user"))

    def test_failed_login(self):
        client = DummyClient("login", "a", "b", "quit")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         (None, None))

    def test_register_user(self):
        client = DummyClient("register", "a", "a", "a")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         ("a", "user"))

    def test_failed_registration(self):
        client = DummyClient("register", "b", "a", "a", "quit")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         (None, None))
        client.counter = -1
        client.messages = ["register", "a", "a", "b", "quit"]
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         (None, None))
    
    def test_anonymous_login(self):
        client = DummyClient("anonymous")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         ("Anonymous", "coward"))

    def test_quit_prompt(self):
        client = DummyClient("invalid_command", "quit")
        database = DummyDatabase()
        self.assertEqual(prompt(client.send, client.recv, client, database),
                         (None, None))
