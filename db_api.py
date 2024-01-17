import sqlite3
from sqlite3 import IntegrityError
import time

connect = sqlite3.connect('db.sqlite')
cursor = connect.cursor()


def add_user(user_id: int):
    try:
        cursor.execute("INSERT INTO USERS VALUES(?, ?, 0)", (user_id, 0))
        connect.commit()
    except IntegrityError:
        pass


def get_user(user_id: int):
    return cursor.execute('SELECT * FROM USERS WHERE user_id = ?', (user_id, )).fetchone()


def update_tries(user_id: int, tries: int):
    cursor.execute('UPDATE USERS SET TRIES = ? WHERE user_id = ?', (tries, user_id))
    connect.commit()


def update_timestamp_user(user_id: int):
    cursor.execute('UPDATE USERS SET TIME = ? where user_id = ?', (int(time.time()), user_id))
    connect.commit()
