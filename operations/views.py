"""View-функции приложения operations (складские операции)."""

import sqlite3
from datetime import date

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from storage import load_products, load_operations, save_operations, save_products
from models.operation import RECEIPT, ISSUE
from services.operation_service import create_operation
from db.database import get_connection


OPERATIONS_FILE = "data/operations.json"
PRODUCTS_FILE = "data/products.json"


# ============================================================
# СТАРЫЕ VIEW-ФУНКЦИИ (JSON) — НЕ УДАЛЯТЬ! Требование ПР7
# ============================================================

def _load_all_operations():
    """Загрузить все операции из JSON со связанными товарами."""
    products_list = load_products(PRODUCTS_FILE)
    products_by_id = {p.id: p for p in products_list}
    return load_operations(OPERATIONS_FILE, products_by_id)


def _load_all_products():
    """Загрузить все товары."""
    return load_products(PRODUCTS_FILE)


def operation_list_json(request) -> HttpResponse:
    """[JSON] Страница списка всех складских операций."""
    ops = _load_all_operations()
    context = {"operations": ops}
    return render(request, "operations/operation_list.html", context)


def operation_detail_json(request, operation_id: int) -> HttpResponse:
    """[JSON] Страница подробной информации об операции."""
    ops = _load_all_operations()
    operation = None
    for op in ops:
        if op.id == operation_id:
            operation = op
            break

    context = {
        "operation": operation,
        "operation_id": operation_id,
    }
    status = 200 if operation is not None else 404
    return render(request, "operations/operation_detail.html", context, status=status)


@require_http_methods(["GET", "POST"])
def operation_receive(request) -> HttpResponse:
    """[JSON] Страница прихода товара на склад."""
    return _operation_form(request, RECEIPT)


@require_http_methods(["GET", "POST"])
def operation_ship(request) -> HttpResponse:
    """[JSON] Страница расхода товара со склада."""
    return _operation_form(request, ISSUE)


def _operation_form(request, operation_type: str) -> HttpResponse:
    """[JSON] Универсальная форма для прихода/расхода."""
    type_label = "Приход" if operation_type == RECEIPT else "Расход"
    icon = "📥" if operation_type == RECEIPT else "📤"
    btn_class = "btn-success" if operation_type == RECEIPT else "btn-warning"

    products_list = _load_all_products()
    context = {
        "products": products_list,
        "type_label": type_label,
        "type_label_lower": type_label.lower(),
        "icon": icon,
        "btn_class": btn_class,
        "error": "",
        "success": "",
    }

    if request.method == "POST":
        product_id_str = request.POST.get("product_id", "").strip()
        quantity_str = request.POST.get("quantity", "").strip()
        op_date_str = request.POST.get("operation_date", "").strip()
        comment = request.POST.get("comment", "").strip()

        if not all([product_id_str, quantity_str, op_date_str]):
            context["error"] = "Товар, количество и дата обязательны."
        else:
            try:
                product_id = int(product_id_str)
                quantity = int(quantity_str)
                day, month, year = map(int, op_date_str.split("."))
                op_date = date(year, month, day)

                product = None
                for p in products_list:
                    if p.id == product_id:
                        product = p
                        break

                if product is None:
                    context["error"] = f"Товар с ID {product_id} не найден."
                else:
                    ops = _load_all_operations()
                    operation = create_operation(
                        ops, product, operation_type, quantity, op_date, comment
                    )
                    if operation is None:
                        context["error"] = (
                            "Операция не выполнена: некорректное количество "
                            "или недостаточно товара."
                        )
                    else:
                        save_operations(OPERATIONS_FILE, ops)
                        save_products(PRODUCTS_FILE, products_list)
                        context["success"] = (
                            f"{type_label}: {quantity} {product.unit} "
                            f"«{product.name}». Новый остаток: {product.stock} {product.unit}."
                        )
            except ValueError:
                context["error"] = "Некорректный формат данных. Проверьте ввод."

    return render(request, "operations/operation_form.html", context)


# ============================================================
# НОВЫЕ VIEW-ФУНКЦИИ (SQLite) — ПР7
# ============================================================

def operation_list(request) -> HttpResponse:
    """[SQLite] История операций с JOIN (названия товаров)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    
    # ИСПРАВЛЕНО: Добавлено o.product_id в выборку
    rows = conn.execute(
        "SELECT o.id, o.product_id, p.name AS product_name, p.article, "
        "o.operation_type, o.quantity, o.operation_date, "
        "o.comment, o.is_cancelled "
        "FROM operations o "
        "JOIN products p ON o.product_id = p.id "
        "ORDER BY o.operation_date DESC, o.id DESC"
    ).fetchall()
    
    conn.close()
    return render(request, "operations/operation_list.html", {"operations": rows})


def operation_detail(request, pk: int) -> HttpResponse:
    """[SQLite] Детали операции с названием товара (JOIN)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT o.*, p.name AS product_name, p.article, p.unit "
        "FROM operations o "
        "JOIN products p ON o.product_id = p.id "
        "WHERE o.id = ?",
        [pk]
    ).fetchone()
    conn.close()

    if row is None:
        return render(request, "operations/operation_detail.html", {"operation": None}, status=404)

    return render(request, "operations/operation_detail.html", {"operation": row})


def operation_statistics(request) -> HttpResponse:
    """[SQLite] Статистика по категориям (GROUP BY + LEFT JOIN + HAVING)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row

    category_stats = conn.execute(
        "SELECT COALESCE(category, 'Без категории') AS category, "
        "SUM(stock) AS total_stock, "
        "COUNT(*) AS product_count "
        "FROM products "
        "GROUP BY category "
        "HAVING total_stock >= 0"
    ).fetchall()

    summary = conn.execute(
        "SELECT SUM(price * stock) AS total_value, "
        "COUNT(*) AS total_products, "
        "SUM(stock) AS total_units "
        "FROM products"
    ).fetchone()

    conn.close()
    return render(request, "operations/statistics.html", {
        "category_stats": category_stats,
        "summary": summary,
    })