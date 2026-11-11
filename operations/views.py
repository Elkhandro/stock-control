"""View-функции приложения operations (складские операции)."""

from datetime import date, datetime

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from storage import load_products, load_operations, save_operations, save_products
from models.operation import RECEIPT, ISSUE
from services.operation_service import create_operation
from operations.models import OPERATION_TYPE_CHOICES, Operation
from products.models import Product


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
# НОВЫЕ VIEW-ФУНКЦИИ (Django ORM) — ПР9
# Раньше здесь были прямые SQL-запросы через sqlite3 (ПР7).
# ============================================================

PAGE_SIZE = 5

# Допустимые варианты сортировки: произвольное значение из URL в order_by() не передаём.
OPERATION_SORT_FIELDS = {
    "date": ("-operation_date", "-id"),
    "date_asc": ("operation_date", "id"),
    "product": ("product__name", "id"),
    "type": ("operation_type", "id"),
}
STATUS_CHOICES = ("active", "cancelled", "all")


def _is_int(value: str) -> bool:
    """Строка — целое неотрицательное число (ASCII-цифры, влезает в INTEGER SQLite)?"""
    return value.isascii() and value.isdigit() and len(value) <= 18


def operation_list(request) -> HttpResponse:
    """[ORM] История операций: фильтры, сортировка, пагинация."""
    error = ""
    operation_date = request.GET.get("date", "").strip()
    selected_product = request.GET.get("product", "").strip()
    selected_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "active")
    sort = request.GET.get("sort", "date")

    if status not in STATUS_CHOICES:
        status = "active"
    if sort not in OPERATION_SORT_FIELDS:
        sort = "date"

    operations_data = (
        Operation.objects
        .annotate(
            product_name=F("product__name"),
            article=F("product__article"),
            unit=F("product__unit"),
        )
        .values(
            "id", "product_id", "product_name", "article", "unit",
            "operation_type", "quantity", "operation_date", "comment", "is_cancelled",
        )
    )

    # Несколько filter() подряд работают как «И».
    if status == "active":
        operations_data = operations_data.filter(is_cancelled=False)
    elif status == "cancelled":
        operations_data = operations_data.filter(is_cancelled=True)

    if operation_date:
        try:
            selected_date = datetime.strptime(operation_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            operations_data = operations_data.filter(operation_date=selected_date)

    if _is_int(selected_product):
        operations_data = operations_data.filter(product_id=int(selected_product))

    if selected_type in dict(OPERATION_TYPE_CHOICES):
        operations_data = operations_data.filter(operation_type=selected_type)

    operations_data = operations_data.order_by(*OPERATION_SORT_FIELDS[sort])

    paginator = Paginator(operations_data, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))  # «abc» -> 1-я страница

    return render(request, "operations/operation_list.html", {
        "operations": page_obj,
        "page_obj": page_obj,
        "operation_date": operation_date,
        "selected_product": selected_product,
        "selected_type": selected_type,
        "status": status,
        "sort": sort,
        "products": Product.objects.order_by("name"),
        "operation_types": OPERATION_TYPE_CHOICES,
        "error": error,
    })


def operation_detail(request, pk: int) -> HttpResponse:
    """[ORM] Детали операции; товар подтягивается одним запросом (select_related)."""
    operation = get_object_or_404(
        Operation.objects.select_related("product"),
        pk=pk,
    )
    return render(request, "operations/operation_detail.html", {"operation": operation})


def operation_statistics(request) -> HttpResponse:
    """[ORM] Статистика склада: сводка, категории, операции по товарам и типам."""
    active_operations = Operation.objects.filter(is_cancelled=False)

    # Статистика строится от Product, поэтому товары без операций не выпадают.
    product_stats = (
        Product.objects
        .annotate(operations_count=Count("operations", filter=Q(operations__is_cancelled=False)))
        .values("name", "article", "operations_count")
        .order_by("-operations_count", "name")
    )

    category_stats = (
        Product.objects
        .values("category")
        .annotate(product_count=Count("id"), total_stock=Sum("stock"))
        .filter(total_stock__gte=0)
        .order_by("category")
    )

    type_stats = (
        active_operations
        .values("operation_type")
        .annotate(operations_count=Count("id"), total_quantity=Sum("quantity"))
        .order_by("operation_type")
    )

    # Товары, по которым нет ни одной активной (не отменённой) операции.
    idle_products = (
        Product.objects
        .exclude(pk__in=active_operations.values_list("product_id", flat=True))
        .order_by("name")
    )

    return render(request, "operations/statistics.html", {
        "summary": Product.objects.summary(),
        "category_stats": category_stats,
        "product_stats": product_stats,
        "type_stats": type_stats,
        "idle_products": idle_products,
    })
