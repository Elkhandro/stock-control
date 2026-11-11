"""Перенос данных из базы ПР7 (``data/stockcontrol.sqlite``) в Django ORM (``db.sqlite3``).

Порядок: Product -> Operation (операции ссылаются на товары).
id записей и связи сохраняются. Скрипт ничего не удаляет, повторный запуск безопасен
(``update_or_create``). Запуск из корня проекта::

    python db/import_sqlite_to_orm.py
    # или
    python -m db.import_sqlite_to_orm
"""

import os
import sqlite3
import sys
from datetime import date, datetime
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockcontrol.settings")

import django  # noqa: E402

django.setup()

# Модели импортируются только после django.setup()
from django.db import transaction  # noqa: E402

from operations.models import Operation  # noqa: E402
from products.models import Product  # noqa: E402

SOURCE_DB = os.path.join(BASE_DIR, "data", "stockcontrol.sqlite")


def parse_date(value: str) -> date:
    """Разобрать дату из базы ПР7: ГГГГ-ММ-ДД или ДД.ММ.ГГГГ (так её писал import_json)."""
    value = value.strip()
    if "." in value:
        return datetime.strptime(value, "%d.%m.%Y").date()
    return date.fromisoformat(value)


def import_data() -> None:
    if not os.path.exists(SOURCE_DB):
        sys.exit(f"Исходная база не найдена: {SOURCE_DB}")

    conn = sqlite3.connect(f"file:{SOURCE_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        products = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        operations = conn.execute("SELECT * FROM operations ORDER BY id").fetchall()
    finally:
        conn.close()

    with transaction.atomic():
        for row in products:
            Product.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "article": row["article"],
                    "category": row["category"] or "Без категории",
                    "unit": row["unit"],
                    "price": Decimal(str(row["price"])),
                    "stock": row["stock"],
                },
            )
        for row in operations:
            Operation.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "product_id": row["product_id"],
                    "operation_type": row["operation_type"],
                    "quantity": row["quantity"],
                    "operation_date": parse_date(row["operation_date"]),
                    "comment": row["comment"] or "",
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )

    print(f"В исходной базе:  товаров {len(products)}, операций {len(operations)}")
    print(
        f"В базе Django:    товаров {Product.objects.count()}, "
        f"операций {Operation.objects.count()}"
    )
    if (len(products), len(operations)) == (
        Product.objects.count(), Operation.objects.count()
    ):
        print("OK: количество записей совпадает.")
    else:
        print("ВНИМАНИЕ: количество записей не совпадает (в базе Django есть другие записи).")


if __name__ == "__main__":
    import_data()
