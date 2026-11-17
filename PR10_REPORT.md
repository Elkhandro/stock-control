# ПР10 — завершение Django-проекта складского учёта

## Адаптация предметной области

Исходный шаблон методички использует Room, User и Booking. В этом репозитории предметная область — склад: Product и Operation. Поэтому требования адаптированы к товарам, остаткам и движениям товара; фиктивные модели бронирования не добавлялись.

## Реализовано

- Django Admin: ProductAdmin с OperationInline, поиском, фильтрами, сортировкой, list_editable, autocomplete_fields, аннотацией числа активных операций и ссылкой на публичную карточку.
- OperationAdmin: поиск, фильтры, autocomplete_fields, select_related, date_hierarchy, редактирование статуса и массовые действия отмены/завершения/возврата в активные.
- OperationQuerySet/OperationManager: active(), cancelled(), completed(), for_date(); методы используются в списке и статистике.
- Статус Operation — CharField с TextChoices ACTIVE/CANCELLED/COMPLETED.
- Миграция operations.0002_operation_status добавляет status, переносит старые значения is_cancelled и затем удаляет старое поле.
- Группа Warehouse Operators создаётся миграцией с разрешениями просмотра/добавления/изменения товаров и операций без права удаления.
- Django Debug Toolbar подключается только при DJANGO_DEBUG=1; URL /__debug__/ и INTERNAL_IPS добавляются в режиме отладки.
- Slug транслитерируется через Unidecode; миграция обновляет slug существующих товаров.
- get_absolute_url используется в ORM-шаблонах; числовой URL оставлен для совместимости.
- LOW_STOCK_THRESHOLD используется в списке товаров и карточках; total_value выводится как GeneratedField.
- Добавлены help_text, локализованные AppConfig.verbose_name, тесты и инструкции демонстрации.

## Миграции

- products.0002_product_slug_total_value — slug и GeneratedField, backfill slug с транслитерацией.
- products.0003_product_stock_help_text — help_text остатка.
- operations.0002_operation_status — перенос is_cancelled в status и удаление старого поля.
- operations.0003_warehouse_operators_group — создание группы Warehouse Operators.

Миграции добавляют/преобразуют поля, не удаляют таблицы товаров и операций. Перед применением к своей базе сделайте резервную копию db.sqlite3.

## Проверки

CI workflow выполняет:
- python manage.py check;
- DJANGO_DEBUG=1 python manage.py check;
- python manage.py makemigrations --check --dry-run --verbosity 3;
- python -m pytest -v.

Последний GitHub Actions workflow завершился успешно: `python manage.py check` — без ошибок; `DJANGO_DEBUG=1 python manage.py check` — без ошибок; `python manage.py makemigrations --check --dry-run --verbosity 3` — без новых миграций; `python -m pytest -v` — 61 passed, 16 subtests passed. Это CI-результат, не запуск на локальном компьютере владельца. Снимки экрана локальной админки и SQL-панели DDT необходимо сделать на машине владельца проекта.

## Локальная демонстрация и скриншоты

См. PR10_shell_demo.md. Для полного отчёта к защите сохраните собственные скриншоты:
1. Product Admin со встроенными операциями и аннотацией.
2. Operation Admin с фильтрами, сортировкой и actions.
3. Debug Toolbar SQL на /operations/, /operations/<id>/ и /admin/.
4. Терминал с check, makemigrations --check и pytest.

## Ветка

Доработки подготовлены в pr10-completion. После зелёного CI их можно слить в main.
