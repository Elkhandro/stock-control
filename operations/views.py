"""View-функции приложения operations (складские операции)."""

from datetime import date

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from storage import load_products, load_operations, save_operations, save_products
from models.operation import RECEIPT, ISSUE
from services.operation_service import create_operation


OPERATIONS_FILE = "data/operations.json"
PRODUCTS_FILE = "data/products.json"


def _load_all_operations():
    """Загрузить все операции из JSON со связанными товарами."""
    products_list = load_products(PRODUCTS_FILE)
    products_by_id = {p.id: p for p in products_list}
    return load_operations(OPERATIONS_FILE, products_by_id)


def _load_all_products():
    """Загрузить все товары."""
    return load_products(PRODUCTS_FILE)


def operation_list(request) -> HttpResponse:
    """Страница списка всех складских операций."""
    ops = _load_all_operations()
    context = {"operations": ops}
    return render(request, "operations/operation_list.html", context)


def operation_detail(request, operation_id: int) -> HttpResponse:
    """Страница подробной информации об операции."""
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
    """Страница прихода товара на склад."""
    return _operation_form(request, RECEIPT)


@require_http_methods(["GET", "POST"])
def operation_ship(request) -> HttpResponse:
    """Страница расхода товара со склада."""
    return _operation_form(request, ISSUE)


def _operation_form(request, operation_type: str) -> HttpResponse:
    """Универсальная форма для прихода/расхода."""
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