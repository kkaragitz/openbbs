"""Interfaces to the BBS's model representation."""

import binascii
import hashlib
import os
import random
import string
import sqlite3
import time

CHARS = string.printable
HASH_ITERATIONS = 500000
SALT_LENGTH = 64


class Database(object):
    """Model and controller implementation for the BBS."""
    def __init__(self, database, operators):
        self.operators = operators.split(",")
        self.connection  = sqlite3.connect(database)
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

    def create_user(self, username, password):
        """Creates a database entry in the users table for the given username
        and password if it does not already exist. Returns True if the entry
        was successfully created.
        """
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?;",
                            (username,))
        if not self.cursor.fetchone():
            status = "sysop" if username in self.operators else "user"
            source = random.SystemRandom(int(time.time()) | os.getpid())
            salt = "".join(source.choice(CHARS) for _ in range(SALT_LENGTH))
            dk = hashlib.pbkdf2_hmac("sha512", password, salt.encode(),
                                     HASH_ITERATIONS)
            self.cursor.execute("INSERT INTO users (username, user_status, "
                                "password, salt, last_login) VALUES "
                                "(?, ?, ?, ?, ?);",
                                (username, status, binascii.hexlify(dk), salt,
                                 time.time()))
            self.connection.commit()
        else:
            status = None
        return status

    def attempt_login(self, username, password):
        """Return the user_status if the given username matches the given 
        password in the users table, otherwise returns None.
        """
        self.cursor.execute("SELECT salt FROM users WHERE username = ?;",
                            (username,))
        result = self.cursor.fetchone()
        if result:
            salt = result[0]
            dk = hashlib.pbkdf2_hmac("sha512", password, salt.encode(),
                                     500000)
            self.cursor.execute("SELECT user_status, last_login FROM users "
                                "WHERE username = ? AND password = ?;",
                                (username, binascii.hexlify(dk)))
            result = self.cursor.fetchone()
            # FIXME: Redundant. <jakob@memeware.net>
            if result:
                status, last_login = result
            else:
                status = last_login = None
            if status == "user" and username in self.operators:
                self.cursor.execute("UPDATE users SET user_status = 'sysop' "
                                    "WHERE username = ?;", (username,))
                self.connection.commit()
                status = "sysop"
            if status is not None:
                self.cursor.execute("UPDATE users SET last_login = ? WHERE "
                                    "username = ?;", (time.time(), username))
                self.connection.commit()
        else:
            status = last_login = None
        return (status, last_login)

    def check_banned(self, username, ip):
        """Query the database to see if a given username or IP is banned, and
        return the reason if it is.
        """
        self.cursor.execute("SELECT reason FROM bans WHERE username = ? OR "
                            "ip = ?;", (username, ip))
        value = self.cursor.fetchone()
        return value[0] if value else None

    def ban_user(self, reason, username=None, ip=None):
        """Adds a username/ip and ban reason to the bans table, returning true
        if the operation was successful.
        """
        self.cursor.execute("INSERT INTO bans (username, ip, reason) VALUES "
                            "(?, ?, ?);", (username, ip, reason))
        self.connection.commit()

    def unban_user(self, username=None, ip=None):
        """Removes a username/ip from the bans table, returning true if the 
        operation was successful.
        """
        self.cursor.execute("DELETE FROM bans WHERE username = ? OR ip = ?;",
                            (username, ip))
        self.connection.commit()

    def make_op(self, username):
        """Makes the given user a sysop on the BBS."""
        self.cursor.execute("UPDATE users SET user_status = 'sysop' WHERE "
                            "username = ?;", (username,))
        self.connection.commit()

    def remove_op(self, username):
        """Makes the given user a standard user on the BBS."""
        self.cursor.execute("UPDATE users SET user_status = 'user' WHERE "
                            "username = ?;", (username,))
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
        """Returns a list of  all of the posts for a given board."""
        if thread:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE post_id = ? OR reply = ? "
                                "ORDER BY post_id ASC;", (thread, thread))
        else:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE board = ? AND reply IS NULL "
                                "ORDER BY post_id DESC;", (board,))
        return self.cursor.fetchall()

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
