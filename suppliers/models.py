from django.db import models


class Supplier(models.Model):
    """Поставщик товаров склада."""

    name = models.CharField("Название компании", max_length=200, unique=True)
    contact_person = models.CharField("Контактное лицо", max_length=150, blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    email = models.EmailField("Электронная почта", blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    notes = models.TextField("Примечание", blank=True)
    image = models.ImageField("Логотип", upload_to="suppliers/", blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True, db_index=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name
