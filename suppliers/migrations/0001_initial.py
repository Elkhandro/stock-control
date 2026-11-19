from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True, verbose_name="Название компании")),
                ("contact_person", models.CharField(blank=True, max_length=150, verbose_name="Контактное лицо")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="Телефон")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Электронная почта")),
                ("address", models.CharField(blank=True, max_length=255, verbose_name="Адрес")),
                ("notes", models.TextField(blank=True, verbose_name="Примечание")),
                ("image", models.ImageField(blank=True, null=True, upload_to="suppliers/", verbose_name="Логотип")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="Активен")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создан")),
            ],
            options={"verbose_name": "Поставщик", "verbose_name_plural": "Поставщики", "ordering": ["name"]},
        ),
    ]
