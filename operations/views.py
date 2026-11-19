"""View-функции приложения operations (складские операции)."""

from datetime import date

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_POST

from operations.forms import OperationFilterForm, OperationForm

from storage import load_products, load_operations, save_operations, save_products
from models.operation import RECEIPT, ISSUE
from services.operation_service import create_operation
from operations.models import OPERATION_TYPE_CHOICES, Operation, OperationStatus, OperationType
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

STATUS_FILTERS = {
    "active": OperationStatus.ACTIVE,
    "cancelled": OperationStatus.CANCELLED,
    "completed": OperationStatus.COMPLETED,
    "all": None,
}


def _is_int(value: str) -> bool:
    """Строка — целое неотрицательное число (ASCII-цифры, влезает в INTEGER SQLite)?"""
    return value.isascii() and value.isdigit() and len(value) <= 18


def operation_list(request) -> HttpResponse:
    """[ORM] Фильтрация операций через GET-форму, сортировка и пагинация."""
    form = OperationFilterForm(request.GET or None, initial={"status": "active", "sort": "date"})
    status = "active"
    sort = "date"
    operations = Operation.objects.active()

    if form.is_bound and form.is_valid():
        data = form.cleaned_data
        status = data.get("status") or "active"
        sort = data.get("sort") or "date"
        if status == "cancelled":
            operations = Operation.objects.cancelled()
        elif status == "completed":
            operations = Operation.objects.completed()
        elif status == "all":
            operations = Operation.objects.all()
        if data.get("date"):
            operations = operations.for_date(data["date"])
        if data.get("product"):
            operations = operations.filter(product=data["product"])
        if data.get("type"):
            operations = operations.filter(operation_type=data["type"])

    operations = operations.annotate(
        product_name=F("product__name"),
        product_slug=F("product__slug"),
        article=F("product__article"),
        unit=F("product__unit"),
    ).values(
        "id", "product_id", "product_name", "product_slug", "article", "unit",
        "operation_type", "quantity", "operation_date", "comment", "status",
    ).order_by(*OPERATION_SORT_FIELDS.get(sort, OPERATION_SORT_FIELDS["date"]))

    paginator = Paginator(operations, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "operations/operation_list.html", {
        "operations": page_obj,
        "page_obj": page_obj,
        "form": form,
        "status": status,
        "error": form.errors.get("date", [""])[0] if form.errors.get("date") else "",
        "sort": sort,
    })


def _apply_stock_change(product_id, operation_type, quantity, reverse=False):
    """Применить или компенсировать влияние операции на остаток товара."""
    receipt_increases = operation_type == OperationType.RECEIPT
    increase = not receipt_increases if reverse else receipt_increases
    queryset = Product.objects.filter(pk=product_id)
    if increase:
        queryset.update(stock=F("stock") + quantity)
    else:
        updated = queryset.filter(stock__gte=quantity).update(stock=F("stock") - quantity)
        if not updated:
            raise ValidationError("Недостаточно товара на складе для выполнения операции.")


@require_http_methods(["GET", "POST"])
def operation_create(request):
    """Создание ORM-операции с атомарным изменением остатка."""
    form = OperationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                operation = form.save(commit=False)
                operation.status = OperationStatus.ACTIVE
                operation.save()
                _apply_stock_change(operation.product_id, operation.operation_type, operation.quantity)
        except ValidationError as exc:
            form.add_error(None, exc.messages[0])
        else:
            messages.success(request, "Складская операция создана, остаток обновлён.")
            return redirect("operations:operation_detail", pk=operation.pk)
    return render(request, "operations/operation_form_django.html", {
        "form": form, "object": None, "title": "Новая складская операция",
    })


@require_http_methods(["GET", "POST"])
def operation_edit(request, pk):
    """Редактирование активной операции с откатом старого и применением нового движения."""
    operation = get_object_or_404(
        Operation.objects.select_related("product"),
        pk=pk, status=OperationStatus.ACTIVE,
    )
    original_product_id = operation.product_id
    original_operation_type = operation.operation_type
    original_quantity = operation.quantity
    form = OperationForm(request.POST or None, instance=operation)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                _apply_stock_change(original_product_id, original_operation_type, original_quantity, reverse=True)
                updated_operation = form.save(commit=False)
                updated_operation.status = OperationStatus.ACTIVE
                updated_operation.save()
                _apply_stock_change(updated_operation.product_id, updated_operation.operation_type, updated_operation.quantity)
        except ValidationError as exc:
            form.add_error(None, exc.messages[0])
        else:
            messages.success(request, "Операция изменена, остаток пересчитан.")
            return redirect("operations:operation_detail", pk=operation.pk)
    return render(request, "operations/operation_form_django.html", {
        "form": form, "object": operation, "title": "Редактирование операции",
    })


@require_POST
def operation_cancel(request, pk):
    """Отмена активной операции через POST с компенсацией изменения остатка."""
    operation = get_object_or_404(Operation, pk=pk, status=OperationStatus.ACTIVE)
    with transaction.atomic():
        _apply_stock_change(operation.product_id, operation.operation_type, operation.quantity, reverse=True)
        operation.status = OperationStatus.CANCELLED
        operation.save(update_fields=["status"])
    messages.success(request, "Операция отменена, остаток восстановлен.")
    return redirect("operations:operation_list")


def operation_detail(request, pk: int) -> HttpResponse:
    """[ORM] Детали операции; товар подтягивается одним запросом (select_related)."""
    operation = get_object_or_404(
        Operation.objects.select_related("product"),
        pk=pk,
    )
    return render(request, "operations/operation_detail.html", {"operation": operation})


def operation_statistics(request) -> HttpResponse:
    """[ORM] Статистика склада: сводка, категории, операции по товарам и типам."""
    active_operations = Operation.objects.active()
    status_stats = Operation.objects.aggregate(
        total_operations=Count("id"),
        active_operations=Count(
            "id", filter=Q(status=OperationStatus.ACTIVE)
        ),
        cancelled_operations=Count(
            "id", filter=Q(status=OperationStatus.CANCELLED)
        ),
        completed_operations=Count(
            "id", filter=Q(status=OperationStatus.COMPLETED)
        ),
    )

    # Статистика строится от Product, поэтому товары без операций не выпадают.
    product_stats = (
        Product.objects
        .annotate(operations_count=Count("operations", filter=Q(operations__status=OperationStatus.ACTIVE)))
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
        "status_stats": status_stats,
    })
