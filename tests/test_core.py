## Tests have been temporarily commented-out to prevent hanging.

# try:
#     import configparser
# except ImportError:
#     import ConfigParser as configparser
# import logging
# import os
# import socket
# import threading
# import unittest

# from asciichan.core import (main, spawn_server)
# from asciichan.config import curry_configuration

# logging.disable(logging.CRITICAL)


# class ServerSpawnTest(unittest.TestCase):
#     def setUp(self):
#         self.config = configparser.ConfigParser()

#     def test_create_server(self):
#         config_get = curry_configuration("none.conf")
#         threading.Thread(target=spawn_server, args=(config_get, True)).start()
#         test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         test_sock.connect((socket.gethostbyname(socket.gethostname()), 1337))
#         self.assertTrue(test_sock.recv(1024))
#         test_sock.close()

#     def test_failure_to_bind(self):
#         with open("temporary.ini", "w+") as temporary:
#             temporary.write("[server]\nhost = 999.999.999.999")
#         config_get = curry_configuration("temporary.ini")
#         with self.assertRaises(SystemExit):
#             spawn_server(config_get, True)
#         os.remove("temporary.ini")
