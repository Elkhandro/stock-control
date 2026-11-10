"""Подключение к базе данных SQLite."""

import sqlite3

DB_PATH = "data/stockcontrol.sqlite"


def get_connection():
    """Вернуть соединение с базой данных с включёнными внешними ключами.

    PRAGMA foreign_keys = ON обязательно: без этой команды
    ограничения внешних ключей в SQLite не проверяются.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn