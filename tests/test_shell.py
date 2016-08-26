import unittest

from openbbs.config import load_config
from openbbs.shell import (ban_user, change_board, change_thread, delete_post,
                           deop_user, get_inbox, get_more, handle_bogus_input,
                           make_post, op_user, refresh_all, send_help_text,
                           send_message, send_rules, send_server_info, shell,
                           unban_user)
from tests.dummy_objects import DummyUser


class AuxiliaryCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_handle_bogus_input(self):
        handle_bogus_input(self.dummy_user, ("bogus",))
        self.assertEqual(self.dummy_user.last_message,
                         "Unknown command: \"bogus\"\r\n")

    def test_send_help_text(self):
        send_help_text(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message[:24],
                         "[D]ELETE\tDelete a post\r\n")

    def test_send_rules(self):
        config = load_config("./inexistent.ini")
        send_rules(self.dummy_user, None, config)
        self.assertEqual(self.dummy_user.last_message, "\r\n")

    def test_send_info(self):
        send_server_info(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message[:22],
                         "OpenBBS Server Version")


class NavigationCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_change_board_with_params(self):
        change_board(self.dummy_user, (None, "random"), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "random")

    def test_change_board_with_commands(self):
        self.dummy_user.messages = ("random",)
        change_board(self.dummy_user, (None,), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "random")

    def test_change_board_return_to_main(self):
        self.dummy_user.messages = ("",)
        change_board(self.dummy_user, (None,), ("random:a",))
        self.assertEqual(self.dummy_user.current_board, "main")

    def test_change_board_invalid_board(self):
        change_board(self.dummy_user, (None, "random"), ("",))
        self.assertEqual(self.dummy_user.current_board, "main")

    def test_change_thread_with_params(self):
        self.dummy_user.current_board = "random"
        change_thread(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.current_thread, "1")

    def test_change_thread_with_commands(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.messages = ("1",)
        change_thread(self.dummy_user, (None,))
        self.assertEqual(self.dummy_user.current_thread, "1")

    def test_change_thread_return_board_home(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.messages = ("",)
        change_thread(self.dummy_user, (None,))
        self.assertEqual(self.dummy_user.current_thread, None)

    def test_change_thread_fail_on_main(self):
        self.dummy_user.current_board = "main"
        change_thread(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.current_thread, None)

    def test_change_thread_fail_on_inexistent_thread(self):
        self.dummy_user.current_board = "random"
        change_thread(self.dummy_user, (None, "2"))
        self.assertEqual(self.dummy_user.current_thread, None)

    def test_refresh_all(self):
        refresh_all(self.dummy_user, None, ["random:a"])
        self.assertTrue(self.dummy_user.last_message)
        self.dummy_user.current_board = "random"
        refresh_all(self.dummy_user, None, ["random:a"])
        self.assertTrue(self.dummy_user.last_message)
        self.dummy_user.current_thread = "1"
        refresh_all(self.dummy_user, None, ["random:a"])
        self.assertTrue(self.dummy_user.last_message)


class PrivateMessagingCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_get_inbox(self):
        get_inbox(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message[119:124],
                         "INBOX")

    def test_get_empty_inbox(self):
        self.dummy_user.name = "DummyUserEmpty"
        get_inbox(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "Your inbox is empty.\r\n")

    def test_get_inbox_fail_on_coward(self):
        self.dummy_user.status = "coward"
        get_inbox(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_get_specific_message_with_params(self):
        get_more(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.last_message[115:129],
                         "Message from a")

    def test_get_specific_message_with_commands(self):
        self.dummy_user.messages = ("1",)
        get_more(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message[115:129],
                         "Message from a")

    def test_get_specific_message_fail_inexistent(self):
        self.dummy_user.name = "DummyUserEmpty"
        get_more(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.last_message,
                         "Message does not exist, or does "
                         "not belong to you.\r\n")

    def test_get_specific_message_fail_on_coward(self):
        self.dummy_user.status = "coward"
        get_more(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_send_message_with_params(self):
        send_message(self.dummy_user, (None, "meme", "a"))
        self.assertEqual(self.dummy_user.last_message,
                         "Message successfully sent.\r\n")

    def test_send_message_with_commands(self):
        self.dummy_user.messages = ("meme2", "a")
        send_message(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "User meme2 does not exist.\r\n")

    def test_send_message_fail_on_coward(self):
        self.dummy_user.status = "coward"
        send_message(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")


class PostingCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_make_post_with_commands(self):
        self.dummy_user.current_board = "random"
        self.dummy_user.current_thread = None
        self.dummy_user.messages = ("a", "a")
        make_post(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "Successfully posted.\r\n")
        self.dummy_user.messages = ("a",)
        self.dummy_user.counter = -1
        self.dummy_user.current_thread = "1"
        make_post(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "Successfully posted.\r\n")

    def test_make_post_fail_on_main(self):
        make_post(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "You can't post on the overboard.\r\n")


class AdministrationCommandsTest(unittest.TestCase):
    def setUp(self):
        self.dummy_user = DummyUser()

    def test_delete_post_with_params(self):
        delete_post(self.dummy_user, (None, "1"))
        self.assertEqual(self.dummy_user.last_message,
                         "Post 1 successfully deleted.\r\n")

    def test_delete_post_with_commands(self):
        self.dummy_user.messages = ("1")
        delete_post(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "Post 1 successfully deleted.\r\n")

    def test_delete_post_fail_on_not_sysop(self):
        self.dummy_user.status = "user"
        delete_post(self.dummy_user, None)
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_ban_user_with_params(self):
        ban_user(self.dummy_user, (None, "meme", "no"))
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully banned.\r\n")

    def test_ban_user_with_commands(self):
        self.dummy_user.messages = ("meme", "no")
        ban_user(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully banned.\r\n")

    def test_ban_user_fail_on_not_sysop(self):
        self.dummy_user.status = "coward"
        ban_user(self.dummy_user, (None, "meme", "no"))
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_unban_user_with_params(self):
        unban_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully unbanned.\r\n")

    def test_unban_user_with_commands(self):
        self.dummy_user.messages = ("meme",)
        unban_user(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully unbanned.\r\n")

    def test_unban_user_fail_on_not_sysop(self):
        self.dummy_user.status = "coward"
        unban_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_op_user_with_params(self):
        op_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully sysop'd.\r\n")

    def test_op_user_with_commands(self):
        self.dummy_user.messages = ("meme",)
        op_user(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully sysop'd.\r\n")

    def test_op_user_fail_on_not_sysop(self):
        self.dummy_user.status = "coward"
        op_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")

    def test_deop_user_with_params(self):
        deop_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully deop'd.\r\n")

    def test_deop_user_with_commands(self):
        self.dummy_user.messages = ("meme",)
        deop_user(self.dummy_user, ())
        self.assertEqual(self.dummy_user.last_message,
                         "User meme successfully deop'd.\r\n")

    def test_deop_user_fail_on_not_sysop(self):
        self.dummy_user.status = "coward"
        deop_user(self.dummy_user, (None, "meme"))
        self.assertEqual(self.dummy_user.last_message,
                         "You can't do that!\r\n")


class CommandInterpreterTest(unittest.TestCase):
    def test_accept_commands(self):
        config = load_config("./inexistent.ini")
        dummy_user = DummyUser("help", "bogus", "quit")
        shell(dummy_user, config)
        self.assertEqual(dummy_user.last_message,
                         config["quit"] + "\r\n")
