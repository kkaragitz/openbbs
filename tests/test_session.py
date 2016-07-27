#!/usr/bin/python

import unittest

import tests.dummy_objects

from asciichan.session import (curry_io, handle)


class IOTest(unittest.TestCase):
    def test_curry_io(self):
        client = tests.dummy_objects.DummyClient()
        database = tests.dummy_objects.DummyDatabase()
        send, receive = curry_io(client, database, "")
        self.assertTrue(receive())


class ClientHandler(unittest.TestCase):
    def setUp(self):
        self.client = tests.dummy_objects.DummyClient()
        self.config = tests.dummy_objects.DummyConfig()

    def test_handler(self):
        self.assertFalse(handle(self.client, "0.0.0.0", self.config))
