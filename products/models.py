"""Django ORM-модель товара (ПР9).

Не путать с пакетом ``models/`` в корне проекта: там лежат обычные
классы предметной области из ПР3 (консольная версия), а здесь — модель
Django, которая хранится в таблице базы данных.
"""

from decimal import Decimal

from django.db import models
from django.db.models import Count, DecimalField, F, Sum

LOW_STOCK_THRESHOLD = 10


class ProductQuerySet(models.QuerySet):
    """Запросы по товарам, которые используются в нескольких представлениях."""

    def summary(self) -> dict:
        """Сводка по складу: стоимость остатков, число товаров, единиц на складе."""
        return self.aggregate(
            total_value=Sum(
                F("price") * F("stock"),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            ),
            total_products=Count("id"),
            total_units=Sum("stock"),
        )


class Product(models.Model):
    """Товар на складе."""

    name = models.CharField("Название", max_length=200)
    article = models.CharField("Артикул", max_length=50, unique=True)
    category = models.CharField("Категория", max_length=100)
    unit = models.CharField("Единица измерения", max_length=20, default="шт.")
    price = models.DecimalField(
        "Цена за единицу", max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    stock = models.PositiveIntegerField("Остаток", default=0)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return self.name

    def get_total_value(self) -> Decimal:
        """Общая стоимость остатка товара (цена × остаток)."""
        return self.price * self.stock

    def is_low_stock(self, threshold: int = LOW_STOCK_THRESHOLD) -> bool:
        """Остаток ниже порога?"""
        return self.stock < threshold

    def check_availability(self, quantity: int = 1) -> bool:
        """Достаточно ли товара на складе для указанного количества."""
        return self.stock >= quantity
