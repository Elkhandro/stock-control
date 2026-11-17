# Generated for ПР10.
from django.db import migrations, models
from django.db.models import F


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(
                blank=True,
                db_index=True,
                max_length=220,
                verbose_name="URL-идентификатор",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="total_value",
            field=models.GeneratedField(
                db_persist=True,
                expression=F("price") * F("stock"),
                output_field=models.DecimalField(decimal_places=2, max_digits=16),
                verbose_name="Стоимость остатка",
            ),
        ),
    ]
