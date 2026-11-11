"""View-функции приложения products (товары)."""

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from storage import load_products, save_products
from services.product_service import (
    add_product,
    find_product,
    find_product_by_id,
    sort_products_by_stock,
)
from products.models import Product


PRODUCTS_FILE = "data/products.json"


# ============================================================
# СТАРЫЕ VIEW-ФУНКЦИИ (JSON) — НЕ УДАЛЯТЬ! Требование ПР7
# ============================================================

def _load_all_products():
    """Загрузить все товары из JSON."""
    return load_products(PRODUCTS_FILE)


def _save_all_products(products):
    """Сохранить все товары в JSON."""
    save_products(PRODUCTS_FILE, products)


def product_list_json(request) -> HttpResponse:
    """[JSON] Страница списка товаров с поиском и сортировкой."""
    products_list = _load_all_products()

    query = request.GET.get("q", "").strip()
    if query:
        products_list = find_product(products_list, query)

    sort_param = request.GET.get("sort", "")
    if sort_param == "stock_asc":
        products_list = sort_products_by_stock(products_list, reverse=False)
    elif sort_param == "stock_desc":
        products_list = sort_products_by_stock(products_list, reverse=True)

    context = {
        "products": products_list,
        "query": query,
        "sort": sort_param,
    }
    return render(request, "products/product_list.html", context)


def product_detail_json(request, product_id: int) -> HttpResponse:
    """[JSON] Страница подробной информации о товаре."""
    products_list = _load_all_products()
    product = find_product_by_id(products_list, product_id)

    context = {
        "product": product,
        "product_id": product_id,
    }

    if product is not None:
        context["info"] = product.get_info()
        status = 200
    else:
        status = 404

    return render(request, "products/product_detail.html", context, status=status)


@require_http_methods(["GET", "POST"])
def product_add(request) -> HttpResponse:
    """[JSON] Страница добавления нового товара."""
    context = {"error": "", "success": ""}

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        article = request.POST.get("article", "").strip()
        category = request.POST.get("category", "").strip()
        unit = request.POST.get("unit", "").strip()
        price_str = request.POST.get("price", "").strip()
        stock_str = request.POST.get("stock", "0").strip()

        if not all([name, article, category, unit, price_str]):
            context["error"] = "Все поля кроме остатка обязательны."
        else:
            try:
                price = float(price_str)
                stock = int(stock_str) if stock_str else 0
                products_list = _load_all_products()
                new_product = add_product(
                    products_list, name, article, category, unit, price, stock
                )
                _save_all_products(products_list)
                context["success"] = (
                    f"Товар «{new_product.name}» добавлен с ID {new_product.id}."
                )
            except ValueError:
                context["error"] = "Цена должна быть числом, остаток — целым числом."

    return render(request, "products/product_add.html", context)


# ============================================================
# НОВЫЕ VIEW-ФУНКЦИИ (Django ORM) — ПР9
# Раньше здесь были прямые SQL-запросы через sqlite3 (ПР7).
# ============================================================

# Допустимые варианты сортировки: произвольное значение из URL в order_by() не передаём.
PRODUCT_SORT_FIELDS = {
    "name": ("name",),
    "category": ("category", "name"),
    "stock_asc": ("stock", "name"),
    "stock_desc": ("-stock", "name"),
}


def _is_int(value: str) -> bool:
    """Строка — целое неотрицательное число (ASCII-цифры, влезает в INTEGER SQLite)?"""
    return value.isascii() and value.isdigit() and len(value) <= 18


def product_list(request) -> HttpResponse:
    """[ORM] Список товаров: поиск по названию/артикулу и сортировка."""
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "name")
    if sort not in PRODUCT_SORT_FIELDS:
        sort = "name"

    products_qs = Product.objects.all()
    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) | Q(article__icontains=query)
        )
    products_qs = products_qs.order_by(*PRODUCT_SORT_FIELDS[sort])

    return render(request, "products/product_list.html", {
        "products": products_qs,
        "query": query,
        "sort": sort,
    })


def product_detail(request, pk: int) -> HttpResponse:
    """[ORM] Карточка товара + история его операций (обратная связь product.operations)."""
    product = get_object_or_404(Product, pk=pk)
    operations = product.operations.order_by("-operation_date", "-pk")
    return render(request, "products/product_detail.html", {
        "product": product,
        "operations": operations,
    })


def product_search(request) -> HttpResponse:
    """[ORM] Поиск товаров: максимальный остаток, категория, начало артикула."""
    max_stock = request.GET.get("max_stock", "").strip()
    category = request.GET.get("category", "").strip()
    article = request.GET.get("article", "").strip()

    searched = bool(max_stock or category or article)
    products_qs = Product.objects.none()

    if searched:
        products_qs = Product.objects.all()
        if _is_int(max_stock):
            products_qs = products_qs.filter(stock__lte=int(max_stock))
        if category:
            products_qs = products_qs.filter(category__iexact=category)
        if article:
            products_qs = products_qs.filter(article__istartswith=article)
        products_qs = products_qs.order_by("stock", "name")

    categories = (
        Product.objects.order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    return render(request, "products/product_search.html", {
        "products": products_qs,
        "max_stock": max_stock,
        "category": category,
        "article": article,
        "categories": categories,
        "searched": searched,
    })
