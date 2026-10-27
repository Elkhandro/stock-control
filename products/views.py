"""View-функции приложения products (товары)."""

from django.http import HttpResponse

from homepage.views import page
from storage import load_products
from services.product_service import find_product_by_id


def _load_all_products():
    """Загрузить все товары из JSON."""
    return load_products("data/products.json")


def product_list(request) -> HttpResponse:
    """Страница списка всех товаров."""
    products_list = _load_all_products()

    if not products_list:
        content = '<div class="alert alert-info">Товаров пока нет.</div>'
        return page("Товары", content)

    rows = ""
    for p in products_list:
        stock_badge = (
            "bg-success" if p.stock >= 10 else "bg-danger"
        )
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

    content = f"""
    <h1 class="mb-4">📦 Товары на складе</h1>
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
        return HttpResponse(page("Товар не найден", content).content, status=404)

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