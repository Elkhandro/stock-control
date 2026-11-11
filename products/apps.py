from django.apps import AppConfig
from django.db.backends.signals import connection_created


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Регистронезависимый поиск по кириллице в SQLite (icontains, iexact, ...)
        from db.sqlite_like import register_unicode_like

        connection_created.connect(register_unicode_like)
