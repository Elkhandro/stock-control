"""View-функции приложения homepage."""

from django.http import HttpResponse


def page(title: str, content: str, status: int = 200) -> HttpResponse:
    """Единый HTML-каркас с Bootstrap 5.3 через CDN."""
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Складской учёт</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet"
          integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YcnS/1p8TQ5F2yGnFhM2kC3pE6fKJlBbNj"
          crossorigin="anonymous">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">📦 Складской учёт</a>
            <button class="navbar-toggler" type="button"
                    data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Главная</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/products/">Товары</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/products/add/">+ Товар</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/operations/">Операции</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/operations/receive/">📥 Приход</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/operations/ship/">📤 Расход</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mb-5">
        {content}
    </div>
    <footer class="text-center text-muted py-3 border-top">
        <small>Складской учёт &copy; 2026 | PR5 Django</small>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
            crossorigin="anonymous"></script>
</body>
</html>"""
    return HttpResponse(html, status=status)


def index(request) -> HttpResponse:
    """Главная страница склада."""
    from storage import load_products, load_operations

    products_list = load_products("data/products.json")
    operations_list_raw = load_operations(
        "data/operations.json",
        {p.id: p for p in products_list},
    )

    total_value = sum(p.get_total_value() for p in products_list)
    low_stock = [p for p in products_list if p.stock < 10]
    active_ops = [op for op in operations_list_raw if not op.is_cancelled]

    content = f"""
    <h1 class="mb-4">Центральный склад🏭</h1>
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card text-bg-primary h-100">
                <div class="card-body">
                    <h4 class="card-title">Товаров на складе</h4>
                    <p class="display-6">{len(products_list)}</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-bg-success h-100">
                <div class="card-body">
                    <h4 class="card-title">Общая стоимость</h4>
                    <p class="display-6">{total_value:,.2f} ₽</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-bg-warning h-100">
                <div class="card-body">
                    <h4 class="card-title">Активных операций</h4>
                    <p class="display-6">{len(active_ops)}</p>
                </div>
            </div>
        </div>
    </div>
    """

    if low_stock:
        items = "".join(
            f'<li class="list-group-item d-flex justify-content-between">'
            f'<span>{p.name}</span>'
            f'<span class="badge bg-danger">{p.stock} {p.unit}</span>'
            f"</li>"
            for p in low_stock
        )
        content += f"""
        <div class="card border-danger mb-4">
            <div class="card-header bg-danger text-white">
                Товары с низким остатком (&lt; 10 шт.)⚠️
            </div>
            <ul class="list-group list-group-flush">{items}</ul>
        </div>
        """
    else:
        content += """
        <div class="alert alert-success">
            ✅ Все товары имеют достаточный остаток.
        </div>
        """

    return page("Главная", content)


def page_not_found(request, exception) -> HttpResponse:
    """Кастомная страница 404."""
    content = """
    <div class="text-center py-5">
        <h1 class="display-1 text-muted">404</h1>
        <h2 class="mb-3">Страница не найдена</h2>
        <p class="lead text-muted">Запрашиваемый ресурс не существует.</p>
        <a href="/" class="btn btn-primary mt-3">Вернуться на главную</a>
    </div>
    """
    return page("Ошибка 404", content)