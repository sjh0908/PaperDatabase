# database/db.py
import pymysql

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    MYSQL_CHARSET
)


def get_connection():
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset=MYSQL_CHARSET,

        cursorclass=pymysql.cursors.DictCursor,

        autocommit=False
    )

    return connection

def commit(connection):
    connection.commit()

def rollback(connection):
    connection.rollback()

def close_connection(connection):
    if connection is not None:
        connection.close()