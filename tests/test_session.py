#!/usr/bin/python

import unittest

import tests.dummy_objects

import asciichan.session


class IOTest(unittest.TestCase):
    def test_curry_io(self):
        client = tests.dummy_objects.DummyClient()
        send, receive = asciichan.session.curry_io(client)
        self.assertTrue(receive())


class ClientHandler(unittest.TestCase):
    def setUp(self):
        self.client = tests.dummy_objects.DummyClient()
        self.config = tests.dummy_objects.DummyConfig()

    def test_handler(self):
        self.assertFalse(asciichan.session.handle(self.client, "0.0.0.0",
                                                  self.config))
