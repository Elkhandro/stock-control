"""View-функции приложения operations (складские операции)."""

from django.http import HttpResponse

from homepage.views import page
from storage import load_products, load_operations
from models.operation import RECEIPT


def _load_all_operations():
    """Загрузить все операции из JSON со связанными товарами."""
    products_list = load_products("data/products.json")
    products_by_id = {p.id: p for p in products_list}
    return load_operations("data/operations.json", products_by_id)


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
    <h1 class="mb-4">📋 История складских операций</h1>
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
        return HttpResponse(
            page("Операция не найдена", content).content, status=404
        )

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