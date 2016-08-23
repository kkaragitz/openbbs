import os
import unittest

from openbbs.config import load_config


class ConfigurationCreationTest(unittest.TestCase):
    def test_config_defaults(self):
        config = load_config("inexistent.conf")
        self.assertTrue(config.get("name", False))

    def test_file_override(self):
        with open("temporary.ini", "w+") as temporary:
            temporary.write("[server]\nhost = 192.168.1.12")
        config = load_config("temporary.ini")
        self.assertEqual(config.get("host"), "192.168.1.12")
        os.remove("temporary.ini")
