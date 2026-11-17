"""Общие данные склада для всех Django-шаблонов."""


def warehouse_context(request):
    """Возвращает единое название склада и порог низкого остатка."""
    from products.models import LOW_STOCK_THRESHOLD

    return {
        "WAREHOUSE_NAME": "Центральный склад",
        "LOW_STOCK_THRESHOLD": LOW_STOCK_THRESHOLD,
    }
