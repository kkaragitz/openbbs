import os
import unittest

from asciichan.config import curry_configuration


class ConfigurationCurryTest(unittest.TestCase):
    def test_config_get(self):
        with open("temporary.ini", "w+") as temporary:
            temporary.write("[server]\nhost = 192.168.1.12")
        config_get = curry_configuration("temporary.ini")
        self.assertEqual(config_get("server", "host"), "192.168.1.12")
        self.assertEqual(config_get("a", "b", default="c"), "c")
        self.assertEqual(config_get("a", "b"), None)
        os.remove("temporary.ini")
