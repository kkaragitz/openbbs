import logging
import socket
import threading
import unittest

from asciichan.core import (main, spawn_server)

logging.disable(logging.CRITICAL)


class ServerSpawnTest(unittest.TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()

    def test_create_server(self):
        threading.Thread(target=spawn_server, args=(self.config, True)).start()
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.connect((socket.gethostbyname(socket.gethostname()), 1337))
        self.assertTrue(test_sock.recv(1024))
        test_sock.close()

    def test_failure_to_bind(self):
        self.config.add_section("server")
        self.config.set("server", "host", "999.999.999.999")
        with self.assertRaises(SystemExit):
            spawn_server(self.config, True)
        self.config.remove_section("server")
