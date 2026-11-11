"""Просмотр исходной базы ПР7 (только чтение).

Выводит таблицы, столбцы (имя, тип, NOT NULL, PK) и число записей
в ``data/stockcontrol.sqlite``. Запуск из корня проекта::

    python db/inspect_source_db.py
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DB = os.path.join(BASE_DIR, "data", "stockcontrol.sqlite")


def main() -> None:
    if not os.path.exists(SOURCE_DB):
        print(f"Файл не найден: {SOURCE_DB}")
        sys.exit(1)

    # Открываем в режиме «только чтение», чтобы случайно ничего не изменить.
    conn = sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True)
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        print(f"База: {SOURCE_DB}")
        for table in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            print(f"\nТаблица {table}: {count} записей")
            print(f"  {'столбец':<16}{'тип':<10}{'NOT NULL':<10}PK")
            for _, name, col_type, not_null, _, pk in conn.execute(
                f'PRAGMA table_info("{table}")'
            ):
                print(f"  {name:<16}{col_type:<10}{'да' if not_null else 'нет':<10}"
                      f"{'да' if pk else ''}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
