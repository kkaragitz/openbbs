"""Absctracted interfaces for the BBS database model."""

import binascii
import hashlib
import os
import random
import string
import sqlite3
import time

CHARS = string.printable


def generate_salt(salt_length):
    """Generates a salt of the given salt length."""
    source = random.SystemRandom(int(time.time()) | os.getpid())
    return "".join(source.choice(CHARS) for _ in range(salt_length)).encode()


def hash_password(password, salt, hash_iterations):
    """Hashes a given password with the given salt over a specified
    number of hash iterations.
    """
    key = hashlib.pbkdf2_hmac("sha512", password, salt, hash_iterations)
    return binascii.hexlify(key)


class Database(object):
    """Class representation of the BBS database model, containing
    various methods to abstract from otherwise complicated SQL
    transactions.
    """
    def __init__(self, config):
        self.config = config
        self.connection = sqlite3.connect(config.get("database"))
        self.cursor = self.connection.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS posts (post_id "
                            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, time "
                            "INTEGER NOT NULL, board TEXT NOT NULL, name TEXT "
                            "NOT NULL, subject TEXT, body TEXT NOT NULL, "
                            "reply INTEGER);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id "
                            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                            "username TEXT NOT NULL, user_status TEXT NOT "
                            "NULL, password TEXT NOT NULL, salt TEXT NOT "
                            "NULL, last_login INTEGER NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS bans (ban_no "
                            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                            "username TEXT, ip TEXT, reason TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pms (sender TEXT NOT "
                            "NULL, receiver TEXT NOT NULL, message TEXT NOT "
                            "NULL, time INTEGER NOT NULL, read INTEGER NOT "
                            "NULL);")

        if config.get("max_message_age"):
            age_max = time.time() - float(config.get("max_message_age"))
            self.cursor.execute("DELETE FROM pms WHERE time <= ? AND read;",
                                (age_max,))

        self.connection.commit()

    def create_user(self, name, password):
        """Creates a database entry in the users table for the given
        user information, provided that it does not already exist.
        Returns the user status if the entry was successfully created.
        """
        self.cursor.execute("SELECT * FROM users WHERE username = ?;", (name,))
        if not self.cursor.fetchone():
            status = "sysop" if name in self.config.get("operators") else "user"

            salt_length = int(self.config.get("salt_length"))
            hash_iterations = int(self.config.get("hash_iterations"))

            salt = generate_salt(salt_length)
            hashed = hash_password(password, salt, hash_iterations)
            self.cursor.execute("INSERT INTO users (username, user_status, "
                                "password, salt, last_login) VALUES "
                                "(?, ?, ?, ?, ?);",
                                (name, status, hashed, salt, time.time()))

            self.connection.commit()
        else:
            status = None

        return status

    def attempt_login(self, name, password):
        """Return the user_status if the given username and password
        match, otherwise returns None.
        """
        self.cursor.execute("SELECT salt FROM users WHERE username = ?;",
                            (name,))
        result = self.cursor.fetchone()
        if result:
            hash_iterations = int(self.config.get("hash_iterations"))

            hashed = hash_password(password, result[0], hash_iterations)
            self.cursor.execute("SELECT user_status, last_login FROM users "
                                "WHERE username = ? AND password = ?;",
                                (name, hashed))
            result = self.cursor.fetchone()

            if result:
                status, last_login = result
            else:
                status = last_login = None
            if status == "user" and name in self.config.get("operators"):
                self.cursor.execute("UPDATE users SET user_status = 'sysop' "
                                    "WHERE username = ?;", (name,))
                self.connection.commit()
                status = "sysop"
            if status is not None:
                self.cursor.execute("UPDATE users SET last_login = ? WHERE "
                                    "username = ?;", (time.time(), name))
                self.connection.commit()
        else:
            status = last_login = None

        return (status, last_login)

    def check_banned(self, name, ip_address):
        """Query the database to see if a given username or IP is banned, and
        return the reason if it is.
        """
        self.cursor.execute("SELECT reason FROM bans WHERE username = ? OR "
                            "ip = ?;", (name, ip_address))
        value = self.cursor.fetchone()
        return value[0] if value else None

    def ban_user(self, reason, name=None, ip_address=None):
        """Adds a username/ip and ban reason to the bans table, returning true
        if the operation was successful.
        """
        self.cursor.execute("INSERT INTO bans (username, ip, reason) VALUES "
                            "(?, ?, ?);", (name, ip_address, reason))
        self.connection.commit()

    def unban_user(self, name=None, ip_address=None):
        """Removes a username/ip from the bans table, returning true if the
        operation was successful.
        """
        self.cursor.execute("DELETE FROM bans WHERE username = ? OR ip = ?;",
                            (name, ip_address))
        self.connection.commit()

    def make_op(self, name):
        """Promotes the given username to a status of sysop."""
        self.cursor.execute("UPDATE users SET user_status = 'sysop' WHERE "
                            "username = ?;", (name,))
        self.connection.commit()

    def remove_op(self, name):
        """Makes the given user a standard user on the BBS."""
        self.cursor.execute("UPDATE users SET user_status = 'user' WHERE "
                            "username = ?;", (name,))
        self.connection.commit()

    def delete_post(self, post_id):
        """Deletes the post located at the given ID."""
        self.cursor.execute("DELETE FROM posts WHERE post_id = ?;", (post_id,))
        self.connection.commit()

    def get_post_count(self, last_login=0):
        """Returns the number of posts currently in the BBS's database if a
        board is unspecified, otherwise returns the number of posts in that
        board.
        """
        self.cursor.execute("SELECT COUNT(post_id) FROM posts WHERE time > ?;",
                            (last_login,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_posts(self, board, thread=None):
        """Returns a list of all posts on a given board, or a list of
        replies in a thread if a thread number is specified.
        """
        if thread:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE post_id = ? AND reply is "
                                "NULL OR reply = ? ORDER BY post_id ASC;",
                                (thread, thread))
            posts = self.cursor.fetchall()
        else:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE board = ? AND reply IS NULL "
                                "ORDER BY post_id DESC;", (board,))
            posts = self.cursor.fetchall()
        return posts

    def make_post(self, name, subject, body, board, reply=None):
        """Creates a database entry for the given post information."""
        self.cursor.execute("INSERT INTO posts (time, name, board, subject, "
                            "body, reply) VALUES (?, ?, ?, ?, ?, ?);",
                            (time.time(), name, board, subject, body, reply))
        self.connection.commit()

    def send_pm(self, sender, receiver, message):
        """Generate a database entry for a private message with the given
        sender, receiver and message if the receiver exists.
        """
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?;",
                            (receiver,))
        if self.cursor.fetchone():
            self.cursor.execute("INSERT INTO pms (sender, receiver, message, "
                                "time, read) VALUES (?, ?, ?, ?, 0);",
                                (sender, receiver, message, time.time()))
            self.connection.commit()
            return True

    def get_pm_count(self, receiver):
        """Get the number of PM's in the receiver's inbox."""
        self.cursor.execute("SELECT COUNT(*) FROM pms WHERE receiver = ? AND "
                            "read = 0;", (receiver,))
        return self.cursor.fetchone()[0]

    def get_pms(self, receiver):
        """Get all of the PM's sent to the given receiver."""
        self.cursor.execute("SELECT sender, message, time, read FROM pms "
                            "WHERE receiver = ? ORDER BY time DESC;",
                            (receiver,))
        messages = self.cursor.fetchall()
        self.cursor.execute("UPDATE pms SET read = 1 WHERE receiver = ?;",
                            (receiver,))
        self.connection.commit()
        return messages

    def close(self):
        """Closes the current database."""
        self.connection.close()
