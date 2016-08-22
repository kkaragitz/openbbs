import logging
import socket
import threading
import time
import unittest

from openbbs.config import load_config
from openbbs.core import spawn_server

logging.disable(logging.CRITICAL)


class ServerSpawnTest(unittest.TestCase):
    def test_create_server(self):
        config = load_config("inexistent.conf")
        threading.Thread(target=spawn_server, args=(config, True)).start()
        # Connection occurs before binding if the test doesn't sleep. 
        time.sleep(1)
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.connect((socket.gethostbyname(socket.gethostname()), 1337))
        self.assertTrue(test_sock.recv(1024))
        test_sock.send(b"QUIT")
        test_sock.close()

    def test_failure_to_bind(self):
        config = load_config("inexistent.conf")
        config["host"] = "999.999.999.999"
        with self.assertRaises(SystemExit):
            spawn_server(config, True)
