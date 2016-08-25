import unittest

from openbbs.formatters import (box_boards, box_posts, box_thread, scrub_input)


class FormattersTest(unittest.TestCase):
    def test_box_boards(self):
        self.assertTrue(box_boards(("a:b",)))

    def test_box_posts(self):
        self.assertTrue(box_posts(((1, 1, "a", "a", "a"),),))

    def test_box_thread(self):
        self.assertTrue(box_thread(((1, 1, "a", "a", "a"),),))


class InputScrubbingTest(unittest.TestCase):
    def test_remove_single_characters(self):
        text = chr(7) + chr(8) + chr(12) + chr(26) + chr(27) +chr(127)
        self.assertEqual(scrub_input(text), "(Injection Attempt)" * 6)

    def test_remove_form_feed(self):
        text = "\033c"
        self.assertEqual(scrub_input(text), "(Injection Attempt)c")
