"""Django ORM-модель складской операции (ПР9).

Не путать с классом ``StockOperation`` из пакета ``models/`` (ПР3).
"""

from django.db import models

from products.models import Product

RECEIPT = "приход"
ISSUE = "расход"
OPERATION_TYPE_CHOICES = [
    (RECEIPT, "Приход"),
    (ISSUE, "Расход"),
]


class Operation(models.Model):
    """Складская операция (приход или расход товара).

    ``on_delete=PROTECT`` — товар, по которому есть история операций,
    нельзя удалить случайно: история движения товара сохраняется.
    ``related_name="operations"`` — обратный доступ ``product.operations.all()``.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="operations",
        verbose_name="Товар",
    )
    operation_type = models.CharField(
        "Тип операции", max_length=10, choices=OPERATION_TYPE_CHOICES
    )
    quantity = models.PositiveIntegerField("Количество")
    operation_date = models.DateField("Дата операции")
    comment = models.CharField("Комментарий", max_length=255, blank=True, default="")
    is_cancelled = models.BooleanField("Отменена", default=False)

    class Meta:
        ordering = ["-operation_date", "-pk"]
        verbose_name = "Складская операция"
        verbose_name_plural = "Складские операции"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="operation_quantity_positive",
            ),
        ]

    def __str__(self) -> str:
        action = self.get_operation_type_display()
        return (
            f"{action} {self.quantity} {self.product.unit} — {self.product.name} "
            f"({self.operation_date:%d.%m.%Y})"
        )

    def cancel(self) -> bool:
        """Пометить операцию отменённой.

        Returns:
            True, если операция отменена сейчас, False — если уже была отменена.
        """
        if self.is_cancelled:
            return False
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
        return True
