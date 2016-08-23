import unittest

from openbbs.formatters import (box_boards, box_posts, box_thread)


class FormattersTest(unittest.TestCase):
    def test_box_boards(self):
        self.assertTrue(box_boards(("a:b",)))

    def test_box_posts(self):
        self.assertTrue(box_posts(((1, 1, "a", "a", "a"),),))

    def test_box_thread(self):
        self.assertTrue(box_thread(((1, 1, "a", "a", "a"),),))
