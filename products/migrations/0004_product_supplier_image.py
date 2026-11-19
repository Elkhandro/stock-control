import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_product_stock_help_text"),
        ("suppliers", "0001_initial"),
    ]
    operations = [
        migrations.AddField(
            model_name="product",
            name="supplier",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="suppliers.supplier", verbose_name="Поставщик"),
        ),
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="products/", verbose_name="Изображение"),
        ),
    ]
