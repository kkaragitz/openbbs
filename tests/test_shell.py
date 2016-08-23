import unittest

from openbbs.config import load_config
from openbbs.shell import (ban_user, change_board, change_thread, delete_post,
                           deop_user, get_inbox, handle_bogus_input, make_post,
                           op_user, refresh_all, send_help_text, send_message,
                           send_rules, send_server_info, shell, unban_user)
from tests.dummy_objects import DummyUser


class IndividualCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_handle_bogus_input(self):
        self.assertFalse(handle_bogus_input(self.dummy_user, ("bogus",)))

    def test_send_help_text(self):
        self.assertFalse(send_help_text(self.dummy_user, None))

    def test_send_rules(self):
        config = load_config("./inexistent.ini")
        self.assertFalse(send_rules(self.dummy_user, None, config))

    def test_send_info(self):
        self.assertFalse(send_server_info(self.dummy_user, None))

    def test_change_board_with_params(self):
        change_board(self.dummy_user, (None, "random"), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "random")
        self.dummy_user.current_board = "main"

    def test_change_board_with_commands(self):
        self.dummy_user.messages = ("random",)
        change_board(self.dummy_user, (None,), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "random")
        self.dummy_user.counter = -1
        self.dummy_user.messages = []
        self.dummy_user.current_board = "main"

    def test_change_board_return_to_main(self):
        self.dummy_user.messages = ("",)
        change_board(self.dummy_user, (None,), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "main")
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_change_board_invalid_board(self):
        change_board(self.dummy_user, (None, "random"), ("",))
        self.assertEqual(self.dummy_user.current_board, "main")

    def test_change_thread_with_params(self):
        self.dummy_user.current_board = "random"
        change_thread(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.current_thread, "1")
        self.dummy_user.current_board = "main"
        self.dummy_user.current_thread = None

    def test_change_thread_with_commands(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.messages = ("1",)
        change_thread(self.dummy_user, (None,))
        self.assertEqual(self.dummy_user.current_thread, "1")
        self.dummy_user.counter = -1
        self.dummy_user.messages = []
        self.dummy_user.current_board = "main"
        self.dummy_user.current_thread = None

    def test_change_thread_return_board_home(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.messages = ("",)
        change_thread(self.dummy_user, (None,))
        self.assertEqual(self.dummy_user.current_thread, None)
        self.dummy_user.counter = -1
        self.dummy_user.messages = []
        self.dummy_user.current_board = "main"
        self.dummy_user.current_thread = None

    def test_change_thread_fail_on_main(self):
        self.dummy_user.current_board = "main"
        change_thread(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.current_thread, None)

    def test_change_thread_fail_on_inexistent_thread(self):
        self.dummy_user.current_board = "random"
        change_thread(self.dummy_user, (None, "2"))
        self.assertEqual(self.dummy_user.current_thread, None)

    def test_get_inbox(self):
        self.assertFalse(get_inbox(self.dummy_user, None))

    def test_get_empty_inbox(self):
        self.dummy_user.name = "DummyUserEmpty"
        self.assertFalse(get_inbox(self.dummy_user, None))
        self.dummy_user.name = "DummyUser"

    def test_get_inbox_fail_on_coward(self):
        self.dummy_user.status = "coward"
        self.assertFalse(get_inbox(self.dummy_user, None))
        self.dummy_user.status = "sysop"

    def test_make_post_with_commands(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.current_thread = None
        self.dummy_user.messages = ("a", "a")
        self.assertFalse(make_post(self.dummy_user, None))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []
        self.dummy_user.current_thread = "1"
        self.dummy_user.messages = ("a")
        self.assertFalse(make_post(self.dummy_user, None))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_make_post_fail_on_main(self):
        self.dummy_user.current_board = "main"
        self.assertFalse(make_post(self.dummy_user, None))

    def test_refresh_all(self):
        self.dummy_user.current_thread = "1"
        self.assertFalse(refresh_all(self.dummy_user, None, ["random:a"]))
        self.dummy_user.current_thread = None
        self.dummy_user.current_board = "main"
        self.assertFalse(refresh_all(self.dummy_user, None, ["random:a"]))
        self.dummy_user.current_board = "random"
        self.assertFalse(refresh_all(self.dummy_user, None, ["random:a"]))

    def test_send_message_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(send_message(self.dummy_user, (None, "meme", "a")))

    def test_send_message_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("meme2", "a")
        self.assertFalse(send_message(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_send_message_fail_on_coward(self):
        self.dummy_user.status = "coward"
        self.assertFalse(send_message(self.dummy_user, None))
        self.dummy_user.status = "sysop"

    def test_delete_post_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(delete_post(self.dummy_user, (None, "1")))

    def test_delete_post_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("1")
        self.assertFalse(delete_post(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_delete_post_fail_on_not_sysop(self):
        self.dummy_user.status = "user"
        self.assertFalse(delete_post(self.dummy_user, None))
        self.dummy_user.status = "sysop"

    def test_ban_user_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(ban_user(self.dummy_user, (None, "meme", "no")))

    def test_ban_user_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("meme", "no")
        self.assertFalse(ban_user(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_ban_user_fail_on_not_sysop(self):
        self.dummy_user.status = "anonymous"
        self.assertFalse(ban_user(self.dummy_user, (None, "meme", "no")))

    def test_unban_user_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(unban_user(self.dummy_user, (None, "meme")))

    def test_unban_user_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("meme")
        self.assertFalse(unban_user(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_unban_user_fail_on_not_sysop(self):
        self.dummy_user.status = "anonymous"
        self.assertFalse(unban_user(self.dummy_user, (None, "meme")))

    def test_op_user_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(op_user(self.dummy_user, (None, "meme")))

    def test_op_user_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("meme")
        self.assertFalse(op_user(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_op_user_fail_on_not_sysop(self):
        self.dummy_user.status = "anonymous"
        self.assertFalse(op_user(self.dummy_user, (None, "meme")))

    def test_deop_user_with_params(self):
        self.dummy_user.status = "sysop"
        self.assertFalse(deop_user(self.dummy_user, (None, "meme")))

    def test_deop_user_with_commands(self):
        self.dummy_user.status = "sysop"
        self.dummy_user.messages = ("meme")
        self.assertFalse(deop_user(self.dummy_user, ()))
        self.dummy_user.counter = -1
        self.dummy_user.messages = []

    def test_deop_user_fail_on_not_sysop(self):
        self.dummy_user.status = "anonymous"
        self.assertFalse(deop_user(self.dummy_user, (None, "meme")))


class ShellTest(unittest.TestCase):
    def test_accept_commands(self):
        config = load_config("./inexistent.ini")
        dummy_user = DummyUser("help", "bogus", "quit")
        self.assertFalse(shell(dummy_user, config))
