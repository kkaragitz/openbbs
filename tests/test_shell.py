# import unittest

# from tests.dummy_objects import (DummyClient, DummyConfig, DummyDatabase)

# from openbbs.shell import (box_boards, box_posts, box_thread, shell)


# class FormattersTest(unittest.TestCase):
#     def test_box_items(self):
#         self.assertTrue(box_boards(["board:description"]))
#         self.assertTrue(box_posts([[1, 1.0, "a", "a", "a"]]))
#         self.assertTrue(box_thread([[1, 1.0, "a", "a", "a"]]))


# class ShellTest(unittest.TestCase):
#     def test_commands(self):
#         client = DummyClient("quit")
#         database = DummyDatabase()
#         fakeconfig = DummyConfig()
#         self.assertFalse(shell(client.send, client.recv, "a", "user",
#                                database, fakeconfig.fakeget))
