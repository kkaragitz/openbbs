import os
import time
import unittest

from openbbs.database import Database


class DatabaseCreationTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists("./database.db"):
            os.rename("./database.db", "./database.old.db")
        self.database = Database("./database.db", "")

    def tearDown(self):
        os.remove("./database.db")
        if os.path.exists("./database.old.db"):
            os.rename("./database.old.db", "./database.db")

    def test_database_creation(self):
        self.assertTrue(os.path.exists("./database.db"))

    def test_database_table_creation(self):
        self.database.cursor.execute("SELECT name FROM sqlite_master WHERE "
                                     "type='table' AND name='users';")
        self.assertTrue(self.database.cursor.fetchone())
        self.database.cursor.execute("SELECT name FROM sqlite_master WHERE "
                                     "type='table' AND name='posts';")
        self.assertTrue(self.database.cursor.fetchone())
        self.database.cursor.execute("SELECT name FROM sqlite_master WHERE "
                                     "type='table' AND name='bans';")
        self.assertTrue(self.database.cursor.fetchone())
        self.database.cursor.execute("SELECT name FROM sqlite_master WHERE "
                                     "type='table' AND name='pms';")
        self.assertTrue(self.database.cursor.fetchone())

    def test_database_closure(self):
        self.database.close()
        with self.assertRaises(TypeError):
            self.database.cursor()


class DatabaseAccountTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists("./database.db"):
            os.rename("./database.db", "./database.old.db")
        self.database = Database("./database.db", "")

    def tearDown(self):
        if os.path.exists("./database.old.db"):
            os.rename("./database.old.db", "./database.db")

    def test_create_user(self):
        self.database.create_user("jakob", b"memes")
        self.database.cursor.execute("SELECT * FROM users WHERE "
                                     "username='jakob';")
        self.assertTrue(self.database.cursor.fetchone())
        self.assertFalse(self.database.create_user("jakob", b"memes"))

    def test_login_user(self):
        self.database.create_user("jakob", b"memes")
        self.assertTrue(self.database.attempt_login("jakob", b"memes"))
        self.assertEqual(self.database.attempt_login("jakob", b"nenes"),
                         (None, None))
        self.assertEqual(self.database.attempt_login("kakob", b"nenes"),
                         (None, None))

    def test_login_new_op(self):
        self.database.create_user("jakob", b"memes")
        self.database.operators = ["jakob"]
        self.database.attempt_login("jakob", b"memes")
        self.database.cursor.execute("SELECT user_status FROM users WHERE "
                                     "username = 'jakob';")
        self.assertEqual(self.database.cursor.fetchone(), ("sysop",))


    def test_banned_user(self):
        self.database.create_user("jakob", b"memes")
        self.database.ban_user("Test ban.", "jakob", "127.0.0.1")
        self.assertTrue(self.database.check_banned("", "127.0.0.1"))
        self.assertTrue(self.database.check_banned("jakob", ""))
        self.database.unban_user("jakob", "127.0.0.1")
        self.assertFalse(self.database.check_banned("", "127.0.0.1"))
        self.assertFalse(self.database.check_banned("jakob", ""))


    def test_op_user(self):
        self.database.create_user("jakob", b"memes")
        self.database.make_op("jakob")
        self.database.cursor.execute("SELECT user_status FROM users WHERE "
                                     "username=?;", ("jakob",))
        self.assertEqual(self.database.cursor.fetchone()[0], "sysop")
        self.database.remove_op("jakob")
        self.database.cursor.execute("SELECT user_status FROM users WHERE "
                                     "username=?;", ("jakob",))
        self.assertEqual(self.database.cursor.fetchone()[0], "user")


class DatabasePostTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists("./database.db"):
            os.rename("./database.db", "./database.old.db")
        self.database = Database("./database.db", "")
        self.database.make_post("jakob", "Hello!", "Test!", "technology")

    def tearDown(self):
        if os.path.exists("./database.old.db"):
            os.rename("./database.old.db", "./database.db")

    def test_make_posts(self):
        self.assertTrue(self.database.cursor.execute("SELECT * FROM posts WHERE"
                                                     " name='jakob';"))

    def test_get_posts(self):
        self.assertTrue(self.database.get_posts("technology"))
        self.database.make_post("a", "a", "a", "technology")
        self.assertTrue(self.database.get_posts("technology", "1"))

    def test_get_total_post_count(self):
        self.assertEqual(self.database.get_post_count(), 1)

    def test_get_timed_post_count(self):
        self.assertEqual(self.database.get_post_count(0), 1)
        self.assertEqual(self.database.get_post_count(time.time() + 500), 0)

    def test_delete_post(self):
        self.database.delete_post(1)
        self.assertEqual(self.database.get_post_count("technology"), 0)


class DatabasePMTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists("./database.db"):
            os.rename("./database.db", "./database.old.db")
        self.database = Database("./database.db", "")
        self.database.create_user("jakob", b"password")

    def tearDown(self):
        if os.path.exists("./database.old.db"):
            os.rename("./database.old.db", "./database.db")

    def test_send_pm(self):
        self.database.send_pm("sender", "jakob", "Hello!")
        self.assertEqual(self.database.get_pm_count("jakob"), 1)
        self.assertTrue(self.database.get_pms("jakob"))
