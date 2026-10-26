"""Пакет services: функции работы с коллекциями объектов."""

from services.product_service import (
    add_product,
    find_product,
    find_product_by_id,
    filter_low_stock,
    sort_products_by_stock,
    generate_warehouse_report,
)

from services.operation_service import (
    create_operation,
    cancel_operation,
    find_operations_by_product,
)

__all__ = [
    "add_product",
    "find_product",
    "find_product_by_id",
    "filter_low_stock",
    "sort_products_by_stock",
    "generate_warehouse_report",
    "create_operation",
    "cancel_operation",
    "find_operations_by_product",
]