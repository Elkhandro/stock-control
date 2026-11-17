"""Общие данные склада для всех Django-шаблонов."""

from products.models import LOW_STOCK_THRESHOLD, Product


def warehouse_context(request):
    """Название склада, порог низкого остатка и счётчики товаров.

    Данные доступны всем шаблонам, наследующим base.html, поэтому их
    не нужно передавать из каждого представления отдельно.
    """
    return {
        "WAREHOUSE_NAME": "Центральный склад",
        "LOW_STOCK_THRESHOLD": LOW_STOCK_THRESHOLD,
        "products_count": Product.objects.count(),
        "low_stock_count": Product.objects.filter(
            stock__lt=LOW_STOCK_THRESHOLD
        ).count(),
    }