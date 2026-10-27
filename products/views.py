"""View-функции приложения products (товары)."""

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from storage import load_products, save_products
from services.product_service import (
    add_product,
    find_product,
    find_product_by_id,
    sort_products_by_stock,
)


PRODUCTS_FILE = "data/products.json"


def _load_all_products():
    """Загрузить все товары из JSON."""
    return load_products(PRODUCTS_FILE)


def _save_all_products(products):
    """Сохранить все товары в JSON."""
    save_products(PRODUCTS_FILE, products)


def product_list(request) -> HttpResponse:
    """Страница списка товаров с поиском и сортировкой."""
    products_list = _load_all_products()

    # Поиск
    query = request.GET.get("q", "").strip()
    if query:
        products_list = find_product(products_list, query)

    # Сортировка
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


def product_detail(request, product_id: int) -> HttpResponse:
    """Страница подробной информации о товаре."""
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
    """Страница добавления нового товара."""
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