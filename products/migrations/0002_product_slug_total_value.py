# Generated for ПР10.
from django.db import migrations, models
from django.db.models import F
from django.utils.text import slugify


def populate_product_slugs(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all().only('pk', 'name', 'article').iterator():
        name_part = slugify(product.name) or 'product'
        article_part = slugify(product.article) or f'item-{product.pk}'
        Product.objects.filter(pk=product.pk).update(
            slug=f'{name_part}-{article_part}'[:220]
        )


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
        migrations.RunPython(populate_product_slugs, migrations.RunPython.noop),
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
