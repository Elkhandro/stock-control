"""Настройка pytest для Django-тестов (ORM) без плагина pytest-django.

Тесты предметной области из ПР3 (tests/test_product.py, tests/test_operation.py)
в Django не нуждаются; тесты ORM используют тестовую базу в памяти, которая
создаётся из миграций один раз за запуск pytest.
"""

import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockcontrol.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_database():
    from django.db import connection
    from django.test.utils import setup_test_environment, teardown_test_environment

    setup_test_environment()
    old_name = connection.creation.create_test_db(verbosity=0, autoclobber=True)
    yield
    connection.creation.destroy_test_db(old_name, verbosity=0)
    teardown_test_environment()
