"""Module containing everything required to access the BBS database."""

import hashlib
import sqlite3
import time


class Database(object):
    def __init__(self, database, operators):
        self.operators = operators.split(",")
        self.connection  = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS posts (post_id INTEGER"
                            " PRIMARY KEY AUTOINCREMENT NOT NULL, time INTEGER"
                            " NOT NULL, board TEXT NOT NULL, name TEXT NOT "
                            "NULL, subject TEXT, body TEXT NOT NULL, reply "
                            "INTEGER);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER"
                            " PRIMARY KEY AUTOINCREMENT NOT NULL, username "
                            "TEXT NOT NULL, user_status TEXT NOT NULL, "
                            "password TEXT NOT NULL, last_login INTEGER NOT "
                            "NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS bans (ban_no INTEGER"
                            " PRIMARY KEY AUTOINCREMENT NOT NULL, username "
                            "TEXT, ip TEXT, reason TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pms (sender TEXT NOT "
                            "NULL, receiver TEXT NOT NULL, message TEXT NOT "
                            "NULL, read INTEGER NOT NULL);")

    def create_user(self, username, password):
        """Creates a database entry in the users table for the given username
        and password if it does not already exist. Returns True if the entry
        was successfully created.
        """
        self.cursor.execute("SELECT * FROM users WHERE username=?;",
                            (username,))
        if not self.cursor.fetchone():
            status = "sysop" if username in self.operators else "user"
            self.cursor.execute("INSERT INTO users (username, user_status, "
                                "password, last_login) VALUES (?, ?, ?, ?);",
                                (username, status,
                                 hashlib.sha256(password).hexdigest(),
                                 time.time()))
            self.connection.commit()
            return True

    def attempt_login(self, username, password):
        """Return the user_status if the given username matches the given 
        password in the users table, otherwise returns None.
        """
        self.cursor.execute("SELECT user_status, last_login FROM users "
                            "WHERE username=? AND password=?;",
                            (username,
                             hashlib.sha256(password).hexdigest()))
        result = self.cursor.fetchone()
        if result is None:
            result = (None, None)
        else:
            if result[0] == "user" and username in self.operators:
                self.cursor.execute("UPDATE users SET user_status = 'sysop' "
                                    "WHERE username = ?;", (username,))
                result = ("sysop", result[1]) # This is not good.
            self.cursor.execute("UPDATE users SET last_login = ? WHERE "
                                "username = ?;", (time.time(), username))
            self.connection.commit()
        return result

    def check_banned(self, username, ip):
        """Query the database to see if a given username or IP is banned, and
        return the reason if it is.
        """
        self.cursor.execute("SELECT reason FROM bans WHERE username=? OR "
                            "ip=?;", (username, ip))
        value = self.cursor.fetchone()
        if value:
            return value[0]

    def ban_user(self, reason, username=None, ip=None):
        """Adds a username/ip and ban reason to the bans table, returning true
        if the operation was successful.
        """
        self.cursor.execute("SELECT * FROM bans WHERE username=?;",
                            (username,))
        if not self.cursor.fetchone() or not username:
            self.cursor.execute("INSERT INTO bans (username, ip, reason) "
                                "VALUES (?, ?, ?);", (username, ip, reason))
            self.connection.commit()
            return True

    def unban_user(self, username=None, ip=None):
        """Removes a username/ip from the bans table, returning true if the 
        operation was successful.
        """
        self.cursor.execute("DELETE FROM bans WHERE username=? OR ip=?;",
                            (username,ip))
        self.connection.commit()

    def make_op(self, username):
        """Makes the given user a sysop on the BBS."""
        self.cursor.execute("UPDATE users SET user_status='sysop' WHERE "
                            "username=?;", (username,))
        self.connection.commit()

    def remove_op(self, username):
        """Makes the given user a standard user on the BBS."""
        self.cursor.execute("UPDATE users SET user_status='user' WHERE "
                            "username=?;", (username,))
        self.connection.commit()


    def delete_post(self, post_id):
        """Deletes the given post id."""
        self.cursor.execute("DELETE FROM posts WHERE post_id=?;", (post_id,))
        self.connection.commit()

    def get_post_count(self, board=None, last_login=0):
        """Returns the number of posts currently in the BBS's database if a 
        board is unspecified, otherwise returns the number of posts in that 
        board.
        """
        if board:
            self.cursor.execute("SELECT COUNT(post_id) FROM posts WHERE board=? "
                                "AND time>?;", (board, last_login))
        else:
            self.cursor.execute("SELECT COUNT(post_id) FROM posts WHERE time>?;",
                                (last_login,))
        try:
            count = self.cursor.fetchone()[0]
        except TypeError:
            count = 0
        return count

    def get_posts(self, board, thread=None):
        """Returns a list of  all of the posts for a given board."""
        if thread:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE post_id=? OR reply=? ORDER "
                                "BY post_id ASC;",(thread, thread))
        else:
            self.cursor.execute("SELECT post_id, time, name, subject, body "
                                "FROM posts WHERE board=? AND reply IS NULL "
                                "ORDER BY post_id DESC;",(board,))
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
        self.cursor.execute("SELECT user_id FROM users WHERE username=?;",
                            (receiver,))
        if self.cursor.fetchone():
            self.cursor.execute("INSERT INTO pms (sender, receiver, message, "
                                "read) VALUES (?, ?, ?, 0);",
                                (sender, receiver, message))
            self.connection.commit()
            return True

    def get_pm_count(self, receiver):
        """Get the number of PM's in the receiver's inbox."""
        self.cursor.execute("SELECT COUNT(*) FROM pms WHERE receiver=? AND "
                            "read=0;", (receiver,))
        return self.cursor.fetchone()[0]

    def get_pms(self, receiver):
        """Get all of the PM's sent to the given receiver."""
        self.cursor.execute("SELECT sender, message, read FROM pms WHERE "
                            "receiver=?;", (receiver,))
        messages = self.cursor.fetchall()
        self.cursor.execute("UPDATE pms SET read=1 WHERE receiver=?;",
                            (receiver,))
        self.connection.commit()
        return messages

    def close(self):
        """Closes the current database."""
        self.connection.close()
