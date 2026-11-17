"""Django ORM-модель товара (ПР9).

Не путать с пакетом ``models/`` в корне проекта: там лежат обычные
классы предметной области из ПР3 (консольная версия), а здесь — модель
Django, которая хранится в таблице базы данных.
"""

from decimal import Decimal

from django.db import models
from django.db.models import Count, DecimalField, F, Sum
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

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
    stock = models.PositiveIntegerField("Остаток", default=0, help_text="Текущее количество единиц на складе.")
    slug = models.SlugField("URL-идентификатор", max_length=220, blank=True, unique=True)
    total_value = models.GeneratedField(
        expression=F("price") * F("stock"),
        output_field=DecimalField(max_digits=16, decimal_places=2),
        db_persist=True,
        verbose_name="Стоимость остатка",
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Автоматически формировать уникальный URL-slug из названия, артикула и ID."""
        creating = self.pk is None
        if not self.slug and creating:
            super().save(*args, **kwargs)
        if not self.slug:
            name_part = slugify(unidecode(self.name), allow_unicode=False) or "product"
            article_part = slugify(unidecode(self.article), allow_unicode=False) or "item"
            suffix = f"-{self.pk}"
            base = f"{name_part}-{article_part}"
            self.slug = f"{base[:220 - len(suffix)]}{suffix}"
            if creating:
                super().save(update_fields=["slug"])
                return
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"slug"}
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Каноническая ссылка на карточку товара по slug."""
        return reverse("products:product_detail_slug", kwargs={"slug": self.slug})

    def get_total_value(self) -> Decimal:
        """Общая стоимость остатка товара (цена × остаток)."""
        return self.price * self.stock

    def is_low_stock(self, threshold: int = LOW_STOCK_THRESHOLD) -> bool:
        """Остаток ниже порога?"""
        return self.stock < threshold

    def check_availability(self, quantity: int = 1) -> bool:
        """Достаточно ли товара на складе для указанного количества."""
        return self.stock >= quantity
