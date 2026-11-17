from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_product_slug_total_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="stock",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Текущее количество единиц на складе.",
                verbose_name="Остаток",
            ),
        ),
    ]
