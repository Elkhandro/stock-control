"""View-функции приложения homepage."""

from django.shortcuts import render
from django.http import HttpResponse

from storage import load_products, load_operations


def index(request) -> HttpResponse:
    """Главная страница склада."""
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


def page_not_found(request, exception) -> HttpResponse:
    """Кастомная страница 404."""
    return render(
        request,
        "homepage/404.html",
        {"message": "Страница не найдена"},
        status=404,
    )