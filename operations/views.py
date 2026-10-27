"""View-функции приложения operations (складские операции)."""

from datetime import date

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from homepage.views import page
from storage import load_products, load_operations, save_operations
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

    if not ops:
        content = '<div class="alert alert-info">Операций пока нет.</div>'
        return page("Операции", content)

    rows = ""
    for op in ops:
        type_badge = "bg-success" if op.operation_type == RECEIPT else "bg-warning text-dark"
        type_label = "Приход" if op.operation_type == RECEIPT else "Расход"
        status_badge = "bg-secondary" if op.is_cancelled else "bg-primary"
        status_label = "отменена" if op.is_cancelled else "активна"

        rows += f"""
        <tr class="{'table-secondary' if op.is_cancelled else ''}">
            <td><a href="/operations/{op.id}/">{op.id}</a></td>
            <td>
                <a href="/products/{op.product.id}/">{op.product.name}</a>
            </td>
            <td><span class="badge {type_badge}">{type_label}</span></td>
            <td>{op.quantity} {op.product.unit}</td>
            <td>{op.operation_date.strftime('%d.%m.%Y')}</td>
            <td>{op.comment or '—'}</td>
            <td><span class="badge {status_badge}">{status_label}</span></td>
        </tr>
        """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="mb-0">📋 История складских операций</h1>
        <div class="d-flex gap-2">
            <a href="/operations/receive/" class="btn btn-success">📥 Приход</a>
            <a href="/operations/ship/" class="btn btn-warning">📤 Расход</a>
        </div>
    </div>
    <div class="table-responsive">
        <table class="table table-striped table-hover align-middle">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Товар</th>
                    <th>Тип</th>
                    <th>Количество</th>
                    <th>Дата</th>
                    <th>Комментарий</th>
                    <th>Статус</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """
    return page("Операции", content)


def operation_detail(request, operation_id: int) -> HttpResponse:
    """Страница подробной информации об операции."""
    ops = _load_all_operations()
    operation = None
    for op in ops:
        if op.id == operation_id:
            operation = op
            break

    if operation is None:
        content = f"""
        <div class="alert alert-danger">
            ❌ Операция с ID {operation_id} не найдена.
        </div>
        <a href="/operations/" class="btn btn-outline-primary">
            ← Вернуться к списку операций
        </a>
        """
        return page("Операция не найдена", content, status=404)

    type_badge = (
        "bg-success" if operation.operation_type == RECEIPT else "bg-warning text-dark"
    )
    type_label = "Приход" if operation.operation_type == RECEIPT else "Расход"
    status_badge = "bg-secondary" if operation.is_cancelled else "bg-primary"
    status_label = "отменена" if operation.is_cancelled else "активна"

    content = f"""
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/operations/">Операции</a></li>
            <li class="breadcrumb-item active">Операция №{operation.id}</li>
        </ol>
    </nav>
    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h2 class="mb-0">Операция №{operation.id}</h2>
            <span class="badge {status_badge} fs-6">{status_label}</span>
        </div>
        <div class="card-body">
            <table class="table table-borderless">
                <tr>
                    <th width="30%">Товар:</th>
                    <td>
                        <a href="/products/{operation.product.id}/">
                            {operation.product.name}
                        </a>
                        <small class="text-muted">({operation.product.article})</small>
                    </td>
                </tr>
                <tr>
                    <th>Тип операции:</th>
                    <td><span class="badge {type_badge}">{type_label}</span></td>
                </tr>
                <tr>
                    <th>Количество:</th>
                    <td>{operation.quantity} {operation.product.unit}</td>
                </tr>
                <tr>
                    <th>Дата:</th>
                    <td>{operation.operation_date.strftime('%d.%m.%Y')}</td>
                </tr>
                <tr>
                    <th>Комментарий:</th>
                    <td>{operation.comment or '—'}</td>
                </tr>
            </table>
        </div>
    </div>
    <a href="/operations/" class="btn btn-outline-primary">← К списку операций</a>
    """
    return page(f"Операция №{operation.id}", content)


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
    from storage import save_products

    type_label = "Приход" if operation_type == RECEIPT else "Расход"
    icon = "📥" if operation_type == RECEIPT else "📤"
    btn_class = "btn-success" if operation_type == RECEIPT else "btn-warning"

    products_list = _load_all_products()
    error = ""
    success = ""

    if request.method == "POST":
        product_id_str = request.POST.get("product_id", "").strip()
        quantity_str = request.POST.get("quantity", "").strip()
        op_date_str = request.POST.get("operation_date", "").strip()
        comment = request.POST.get("comment", "").strip()

        if not all([product_id_str, quantity_str, op_date_str]):
            error = "Товар, количество и дата обязательны."
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
                    error = f"Товар с ID {product_id} не найден."
                else:
                    ops = _load_all_operations()
                    operation = create_operation(
                        ops, product, operation_type, quantity, op_date, comment
                    )
                    if operation is None:
                        error = (
                            "Операция не выполнена: некорректное количество "
                            "или недостаточно товара."
                        )
                    else:
                        save_operations(OPERATIONS_FILE, ops)
                        save_products(PRODUCTS_FILE, products_list)
                        success = (
                            f"{type_label}: {quantity} {product.unit} "
                            f"«{product.name}». Новый остаток: {product.stock} {product.unit}."
                        )
            except ValueError:
                error = "Некорректный формат данных. Проверьте ввод."

    # Опции селекта товаров
    options = "".join(
        f'<option value="{p.id}">{p.id} — {p.name} (остаток: {p.stock} {p.unit})</option>'
        for p in products_list
    )

    form_html = f"""
    <h1 class="mb-4">{icon} {type_label} товара</h1>
    {"<div class='alert alert-danger'>" + error + "</div>" if error else ""}
    {"<div class='alert alert-success'>" + success + "</div>" if success else ""}
    <div class="card">
        <div class="card-body">
            <form method="post">
                <div class="mb-3">
                    <label class="form-label">Товар *</label>
                    <select name="product_id" class="form-select" required>
                        <option value="">Выберите товар...</option>
                        {options}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Количество *</label>
                    <input type="number" name="quantity" class="form-control"
                           min="1" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Дата (ДД.ММ.ГГГГ) *</label>
                    <input type="text" name="operation_date" class="form-control"
                           placeholder="28.10.2026" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Комментарий</label>
                    <input type="text" name="comment" class="form-control">
                </div>
                <button type="submit" class="btn {btn_class}">{icon} Оформить {type_label.lower()}</button>
                <a href="/operations/" class="btn btn-outline-secondary ms-2">Отмена</a>
            </form>
        </div>
    </div>
    """
    return page(f"{type_label} товара", form_html)