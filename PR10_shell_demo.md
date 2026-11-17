# ПР10 — сценарий демонстрации в терминале

Выполнять из корня проекта в активированном виртуальном окружении.

```bash
# Установка зависимостей (если окружение ещё не подготовлено)
pip install -r requirements.txt

# Проверка конфигурации и миграций
python manage.py check
python manage.py showmigrations
python manage.py migrate --plan

# Применить новую миграцию после резервной копии db.sqlite3
python manage.py migrate

# Тесты и стиль
python -m pytest -v
flake8 .

# Запуск веб-приложения
python manage.py runserver --insecure
```

Открыть в браузере:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/products/`
- `http://127.0.0.1:8000/operations/`
- `http://127.0.0.1:8000/admin/`

Для входа в админку нужен существующий суперпользователь. Если его ещё нет, создать командой `python manage.py createsuperuser`.
