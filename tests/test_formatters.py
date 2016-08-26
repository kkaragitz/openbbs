import unittest

from openbbs.formatters import (box_boards, box_inbox, box_message, box_posts,
                                box_thread, scrub_input)


class FormattersTest(unittest.TestCase):
    def test_box_boards(self):
        self.assertTrue(box_boards(("a:b",)))

    def test_box_posts(self):
        self.assertTrue(box_posts(((1, 1, "a", "a", "a"),),))

    def test_box_thread(self):
        self.assertTrue(box_thread(((1, 1, "a", "a", "a"),),))

    def test_box_inbox(self):
        self.assertTrue(box_inbox(((1, "a", "a", 1, "a"),),))

    def test_box_message(self):
        self.assertTrue(box_message(("aa", "a")))


class InputScrubbingTest(unittest.TestCase):
    def test_remove_single_characters(self):
        text = chr(7) + chr(8) + chr(12) + chr(26) + chr(27) +chr(127)
        self.assertEqual(scrub_input(text), "")

    def test_remove_form_feed(self):
        self.assertEqual(scrub_input("\033c"), "c")
