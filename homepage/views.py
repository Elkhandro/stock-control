"""View-функции приложения homepage."""

import sqlite3
from django.shortcuts import render
from django.http import HttpResponse

from storage import load_products, load_operations
from db.database import get_connection


# ============================================================
# СТАРАЯ VIEW-ФУНКЦИЯ (JSON) — НЕ УДАЛЯТЬ! Требование ПР7
# ============================================================

def index_json(request) -> HttpResponse:
    """[JSON] Главная страница склада."""
    products_list = load_products("data/products.json")
    products_by_id = {p.id: p for p in products_list}
    operations_list = load_operations("data/operations.json", products_by_id)

    total_value = sum(p.get_total_value() for p in products_list)
    low_stock = [p for p in products_list if p.stock < 10]
    active_ops = [op for op in operations_list if not op.is_cancelled]

    context = {
        "products": products_list,
        "total_value": total_value,
        "active_operations": active_ops,
        "low_stock": low_stock,
    }
    return render(request, "homepage/index.html", context)


# ============================================================
# НОВАЯ VIEW-ФУНКЦИЯ (SQLite) — ПР7
# ============================================================

def index(request) -> HttpResponse:
    """[SQLite] Главная страница: статистика + товары с низким остатком."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    # Агрегатная статистика
    summary = conn.execute(
        "SELECT SUM(price * stock) AS total_value, "
        "COUNT(*) AS total_products, "
        "SUM(stock) AS total_units "
        "FROM products"
    ).fetchone()

    # Товары с низким остатком (< 10)
    low_stock = conn.execute(
        "SELECT id, name, article, category, stock, unit "
        "FROM products WHERE stock < 10 "
        "ORDER BY stock ASC LIMIT 10"
    ).fetchall()

    # Количество активных операций
    active_ops_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM operations WHERE is_cancelled = 0"
    ).fetchone()["cnt"]

    conn.close()

    context = {
        "summary": summary,
        "low_stock_products": low_stock,
        "active_operations_count": active_ops_count,
    }
    return render(request, "homepage/index.html", context)


# ============================================================
# 404 — БЕЗ ИЗМЕНЕНИЙ
# ============================================================

def page_not_found(request, exception) -> HttpResponse:
    """Кастомная страница 404."""
    return render(
        request,
        "homepage/404.html",
        {"message": "Страница не найдена"},
        status=404,
    )