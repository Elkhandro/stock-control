"""View-функции приложения products (товары)."""

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from homepage.views import page
from storage import load_products, save_products
from services.product_service import (
    add_product,
    find_product,
    find_product_by_id,
    filter_low_stock,
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

    # Поиск по query-параметру ?q=
    query = request.GET.get("q", "").strip()
    if query:
        products_list = find_product(products_list, query)

    # Сортировка по query-параметру ?sort=stock_asc / stock_desc
    sort_param = request.GET.get("sort", "")
    if sort_param == "stock_asc":
        products_list = sort_products_by_stock(products_list, reverse=False)
    elif sort_param == "stock_desc":
        products_list = sort_products_by_stock(products_list, reverse=True)

    # Форма поиска и сортировки
    search_sort_html = f"""
    <div class="row g-3 mb-4">
        <div class="col-md-6">
            <form method="get" action="/products/" class="d-flex gap-2">
                <input type="text" name="q" class="form-control"
                       placeholder="Поиск по названию или артикулу..."
                       value="{query}">
                <button type="submit" class="btn btn-outline-primary">Найти</button>
                {f'<a href="/products/" class="btn btn-outline-secondary">Сбросить</a>' if query else ''}
            </form>
        </div>
        <div class="col-md-6 d-flex justify-content-md-end align-items-center gap-2">
            <span class="text-muted">Сортировка:</span>
            <a href="/products/?sort=stock_asc{'&q=' + query if query else ''}"
               class="btn btn-sm {'btn-primary' if sort_param == 'stock_asc' else 'btn-outline-secondary'}">
                Остаток ↑
            </a>
            <a href="/products/?sort=stock_desc{'&q=' + query if query else ''}"
               class="btn btn-sm {'btn-primary' if sort_param == 'stock_desc' else 'btn-outline-secondary'}">
                Остаток ↓
            </a>
        </div>
    </div>
    """

    if not products_list:
        content = search_sort_html + '<div class="alert alert-info">Товаров не найдено.</div>'
        return page("Товары", content)

    rows = ""
    for p in products_list:
        stock_badge = "bg-success" if p.stock >= 10 else "bg-danger"
        rows += f"""
        <tr>
            <td><a href="/products/{p.id}/">{p.id}</a></td>
            <td>{p.name}</td>
            <td><code>{p.article}</code></td>
            <td>{p.category}</td>
            <td>
                <span class="badge {stock_badge}">
                    {p.stock} {p.unit}
                </span>
            </td>
            <td>{p.price:,.2f} ₽</td>
            <td>{p.get_total_value():,.2f} ₽</td>
        </tr>
        """

    table_html = f"""
    <div class="table-responsive">
        <table class="table table-striped table-hover align-middle">
            <thead class="table-dark">
                <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Артикул</th>
                    <th>Категория</th>
                    <th>Остаток</th>
                    <th>Цена</th>
                    <th>Стоимость</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """

    content = f"""
    <h1 class="mb-4">📦 Товары на складе</h1>
    {search_sort_html}
    {table_html}
    """
    return page("Товары", content)


def product_detail(request, product_id: int) -> HttpResponse:
    """Страница подробной информации о товаре."""
    products_list = _load_all_products()
    product = find_product_by_id(products_list, product_id)

    if product is None:
        content = f"""
        <div class="alert alert-danger">
            ❌ Товар с ID {product_id} не найден.
        </div>
        <a href="/products/" class="btn btn-outline-primary">
            ← Вернуться к списку товаров
        </a>
        """
        return page("Товар не найден", content, status=404)

    info = product.get_info()
    stock_badge = "bg-success" if product.stock >= 10 else "bg-danger"

    content = f"""
    <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/products/">Товары</a></li>
            <li class="breadcrumb-item active">{product.name}</li>
        </ol>
    </nav>
    <div class="card mb-4">
        <div class="card-header">
            <h2 class="mb-0">{product.name}</h2>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr><th width="40%">ID:</th><td>{info['id']}</td></tr>
                        <tr><th>Артикул:</th><td><code>{info['article']}</code></td></tr>
                        <tr><th>Категория:</th><td>{product.category}</td></tr>
                        <tr><th>Единица:</th><td>{product.unit}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr>
                            <th width="40%">Остаток:</th>
                            <td><span class="badge {stock_badge} fs-5">
                                {info['stock']} {product.unit}
                            </span></td>
                        </tr>
                        <tr><th>Цена:</th><td>{info['price']:,.2f} ₽</td></tr>
                        <tr><th>Стоимость:</th><td>{info['total_value']:,.2f} ₽</td></tr>
                        <tr><th>Статус:</th><td>{info['status']}</td></tr>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <a href="/products/" class="btn btn-outline-primary">← К списку товаров</a>
    """
    return page(product.name, content)


@require_http_methods(["GET", "POST"])
def product_add(request) -> HttpResponse:
    """Страница добавления нового товара (форма + обработка POST)."""
    error = ""
    success = ""

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        article = request.POST.get("article", "").strip()
        category = request.POST.get("category", "").strip()
        unit = request.POST.get("unit", "").strip()
        price_str = request.POST.get("price", "").strip()
        stock_str = request.POST.get("stock", "0").strip()

        if not all([name, article, category, unit, price_str]):
            error = "Все поля кроме остатка обязательны."
        else:
            try:
                price = float(price_str)
                stock = int(stock_str) if stock_str else 0
                products_list = _load_all_products()
                new_product = add_product(
                    products_list, name, article, category, unit, price, stock
                )
                _save_all_products(products_list)
                success = f"Товар «{new_product.name}» добавлен с ID {new_product.id}."
            except ValueError:
                error = "Цена должна быть числом, остаток — целым числом."

    form_html = f"""
    <h1 class="mb-4">➕ Добавить новый товар</h1>
    {"<div class='alert alert-danger'>" + error + "</div>" if error else ""}
    {"<div class='alert alert-success'>" + success + "</div>" if success else ""}
    <div class="card">
        <div class="card-body">
            <form method="post" action="/products/add/">
                <div class="mb-3">
                    <label class="form-label">Название *</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Артикул *</label>
                    <input type="text" name="article" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Категория *</label>
                    <input type="text" name="category" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Единица измерения *</label>
                    <input type="text" name="unit" class="form-control"
                           placeholder="шт., кг, м" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Цена за единицу *</label>
                    <input type="number" name="price" class="form-control"
                           step="0.01" min="0" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Начальный остаток</label>
                    <input type="number" name="stock" class="form-control"
                           value="0" min="0">
                </div>
                <button type="submit" class="btn btn-success">Добавить товар</button>
                <a href="/products/" class="btn btn-outline-secondary ms-2">Отмена</a>
            </form>
        </div>
    </div>
    """
    return page("Добавить товар", form_html)