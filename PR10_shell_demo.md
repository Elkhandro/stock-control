# ПР10 — сценарий локального запуска и демонстрации

Из корня проекта, после активации venv:

```bash
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python -m pytest -v
```

Создать администратора:

```bash
python manage.py createsuperuser
```

Запустить сайт с Debug Toolbar (PowerShell):

```powershell
$env:DJANGO_DEBUG="1"
python manage.py runserver
```

Linux/macOS:

```bash
DJANGO_DEBUG=1 python manage.py runserver
```

Открыть:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/products/
- http://127.0.0.1:8000/operations/
- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/__debug__/

## Создать тестового staff-пользователя и добавить в группу

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
staff, created = User.objects.get_or_create(
    username="warehouse_demo",
    defaults={"email": "warehouse-demo@example.invalid", "is_staff": True},
)
if created:
    staff.set_password("ЗАДАЙТЕ_СВОЙ_ПАРОЛЬ")
    staff.save()
staff.is_staff = True
staff.save(update_fields=["is_staff"])
staff.groups.add(Group.objects.get(name="Warehouse Operators"))
```

Используйте свой пароль, не сохраняйте его в репозитории. Группа не получает права удаления товаров и операций.

## Что снять на скриншоты для отчёта

1. /admin/products/product/ — inline операций, колонка активных операций, редактируемый остаток.
2. /admin/operations/operation/ — фильтры, сортировка статуса, actions.
3. /operations/ — SQL-панель Debug Toolbar и пагинация.
4. /operations/<id>/ — SQL-панель страницы детали.
5. /admin/ — SQL-панель админки.
6. Терминал с выводом check и pytest.

Снимки экрана нужно сделать в локальном браузере после запуска; они не подменяются результатами CI.
