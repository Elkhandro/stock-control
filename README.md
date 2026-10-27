# stock-control / Складской учёт

Консольное приложение и веб-интерфейс для учёта остатков товаров на складе.

## Текущее состояние (PR6)

- ✅ Django 5.2 веб-интерфейс на системе шаблонов
- ✅ Базовый шаблон с наследованием (`extends`, `block`)
- ✅ Переиспользуемые компоненты (`include`)
- ✅ Именованные URL с namespaces
- ✅ Статические файлы (CSS, JS, изображения)
- ✅ Данные хранятся в JSON (ORM не используется)
- ✅ Классы `Product` и `StockOperation` из ПР3

## Назначение

Приложение предназначено для автоматизации учёта остатков товаров на
складе. Оно позволяет вести централизованный контроль наличия продукции,
фиксировать поступление и отгрузку товаров, а также оперативно получать
информацию о текущих остатках для предотвращения дефицита или излишков.

## Целевая аудитория

Кладовщики, менеджеры по закупкам, бухгалтеры материального стола и
владельцы малого и среднего бизнеса, нуждающиеся в простом и быстром
инструменте инвентаризации без использования сложных ERP-систем.

## Предметная область

Складская логистика и управление товарно-материальными запасами (ТМЦ).
Область охватывает процессы хранения, идентификации товаров, учёта их
движения (приход/расход) и формирования отчётности по текущему состоянию
склада.

Именованные URL
Все ссылки используют {% url %} вместо жёстких адресов:
<a href="{% url 'products:product_detail' product.id %}">


Фильтры шаблонов
Используются встроенные фильтры Django:
{{ products|length }} — количество товаров
{{ product.name|default:"Без названия" }} — значение по умолчанию
{{ product.price|floatformat:2 }} — форматирование числа
{{ operation.operation_date|date:"d.m.Y" }} — форматирование даты


View-функции передают контекст в render()

page() удалена — в обновлённом homepage/views.py её нет, все views используют render(). ✅
app_name = "homepage" — в homepage/urls.py прописан явно. ✅
Именованные URL во всех трёх приложениях — app_name + name= везде есть. ✅
Структура homepage/static/homepage/ — правильная вложенность. ✅
findstatic — в списке команд проверки. ✅
Footer с <span id="current-year"> и JS перед </body> — корректно. ✅
Классы .product-card, .stock-status — добавлены в CSS и используются в шаблонах. ✅
Возврат через {% url %} — нигде нет жёстких адресов. ✅
Не трогаем models/, storage.py, консольную версию — не тронуты. ✅
Нет ORM, форм, БД — только JSON и шаблоны. ✅
Новый репозиторий не создавался. ✅




## Технологии
-Python 3.12, Django 5.2
-Bootstrap 5.3 (CDN)
-Система шаблонов Django (extends, block, include, url)
-JSON-файлы как хранилище данных (без ORM)
-Статические файлы (CSS, JS, изображения)



## Основные сущности (ООП-модель, ПР3)

### Класс `Product` (Товар)

**Атрибуты:**

- `id: int` — уникальный идентификатор товара.
- `name: str` — наименование товара.
- `article: str` — артикул товара.
- `category: str` — категория товара.
- `unit: str` — единица измерения (шт., кг и т.п.).
- `price: float` — цена за единицу товара.
- `stock: int` — текущий остаток на складе.

**Методы:**

- `__str__()` — строковое представление товара для вывода.
- `check_availability(quantity: int)` — проверить доступность товара.
- `receive(quantity: int)` — принять товар на склад (увеличить остаток).
- `ship(quantity: int)` — отгрузить товар со склада (уменьшить остаток).
- `get_total_value()` — рассчитать общую стоимость остатков.
- `get_info()` — вернуть подробную информацию о товаре.
- `to_dict()` — преобразовать в словарь для сохранения в JSON.
- `from_dict(data: dict)` — создать объект из словаря (classmethod).

### Класс `StockOperation` (Складская операция)

**Атрибуты:**

- `id: int` — уникальный идентификатор операции.
- `product: Product` — объект товара, к которому относится операция.
- `operation_type: str` — тип операции ("приход" или "расход").
- `quantity: int` — количество товара в операции.
- `operation_date: date` — дата проведения операции.
- `comment: str` — комментарий к операции (необязательно).
- `is_cancelled: bool` — флаг отмены операции.

**Методы:**

- `__str__()` — строковое представление операции.
- `cancel()` — отменить операцию и восстановить остаток товара.
- `get_status()` — вернуть текстовый статус операции.
- `to_dict()` — преобразовать в словарь для сохранения в JSON.
- `from_dict(data, products_by_id)` — создать объект из словаря (classmethod).

## Взаимодействие классов

- `StockOperation.product` хранит **ссылку на объект** `Product`, а не `product_id`.
- При загрузке из JSON `storage.py` находит объект `Product` по `product_id` и связывает его с операцией.
- Метод `cancel()` у операции обращается к `product.receive()` / `product.ship()` для восстановления остатка.

## Возможности

- просмотр и поиск товаров;
- отбор товаров с низким остатком и сортировка по остатку;
- добавление новых товаров;
- просмотр подробной информации о товаре;
- проверка доступности нужного количества товара;
- приём товара на склад (приход);
- отгрузка товара со склада (расход) с проверкой достаточности остатка;
- отмена ранее созданной операции с восстановлением остатка;
- просмотр истории операций;
- отчёт по складу: общая стоимость остатков и товары с низким остатком;
- хранение данных между запусками приложения.

## Структура проекта

stock-control/
│
├── manage.py                          
├── main.py                            
├── storage.py                         
├── utils.py                           
├── requirements.txt                   
├── README.md                          
├── setup.cfg
├── .gitignore
│
├── stockcontrol/                      
│   ├── __init__.py
│   ├── settings.py                    
│   ├── urls.py                        
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/                         
│   ├── base.html                      
│   └── includes/
│       ├── navigation.html           
│       └── footer.html                
│
├── homepage/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py                       
│   ├── urls.py                        
│   ├── migrations/
│   ├── templates/                     
│   │   └── homepage/
│   │       ├── index.html             
│   │       └── 404.html               
│   └── static/                        
│       └── homepage/
│           ├── css/style.css          
│           ├── js/main.js             
│           └── img/logo.png           
│
├── products/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py                       
│   ├── urls.py                        
│   ├── migrations/
│   └── templates/                    
│       └── products/
│           ├── product_list.html      
│           ├── product_detail.html    
│           ├── product_add.html       
│           └── includes/
│               └── product_card.html  
│
├── operations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py                       
│   ├── urls.py                        
│   ├── migrations/
│   └── templates/                     
│       └── operations/
│           ├── operation_list.html    
│           ├── operation_detail.html  
│           ├── operation_form.html    
│           └── includes/
│               └── operation_status.html 
│
├── models/                            
│   ├── __init__.py
│   ├── product.py
│   └── operation.py                   
│
├── services/                          
│   ├── __init__.py
│   ├── product_service.py
│   └── operation_service.py
│
├── data/                              
│   ├── products.json
│   └── operations.json
│
└── tests/                             
    ├── test_product.py
    └── test_operation.py

## Назначение модулей

### `main.py`

Точка запуска программы: отображение меню, получение данных от
пользователя, вызов функций проекта, обработка исключений на уровне
пользовательского сценария. Работает с коллекциями объектов
`list[Product]` и `list[StockOperation]`.

### `models/`

Пакет с классами предметной области.

- **`product.py`** — класс `Product` с методами изменения и проверки остатка.
- **`operation.py`** — класс `StockOperation` с методом отмены операции.

### `services/`

Пакет с функциями работы с коллекциями объектов.

- **`product_service.py`** — функции `add_product()`, `find_product()`,
  `find_product_by_id()`, `filter_low_stock()`, `sort_products_by_stock()`,
  `generate_warehouse_report()`. Работают с `list[Product]`.
- **`operation_service.py`** — функции `create_operation()`,
  `cancel_operation()`, `find_operations_by_product()`.
  Работают с `list[StockOperation]`.

### `storage.py`

Загрузка и сохранение данных: чтение и запись JSON-файлов через
контекстный менеджер `with`, обработка отсутствия файла и
некорректного JSON. Преобразование между словарями и объектами
выполняется **только** в этом модуле.

## Веб-страницы и URL

| URL                 | View-функция                        | Описание                                      |
| ------------------- | ----------------------------------- | --------------------------------------------- |
| `/`                 | `homepage.views.index`              | Главная: статистика, товары с низким остатком |
| `/products/`        | `products.views.product_list`       | Список всех товаров                           |
| `/products/<id>/`   | `products.views.product_detail`     | Карточка товара                               |
| `/operations/`      | `operations.views.operation_list`   | История операций                              |
| `/operations/<id>/` | `operations.views.operation_detail` | Детали операции                               |
| Любой другой        | `homepage.views.page_not_found`     | Кастомная 404                                 |

## Формат хранения данных

Формат JSON сохранён из ПР2. Товары (`data/products.json`) — список словарей:

````json
[
    {
        "id": 1,
        "name": "Ноутбук Lenovo",
        "article": "NB-001",
        "category": "Электроника",
        "unit": "шт.",
        "price": 75000.5,
        "stock": 15
    }
]

## Установка зависимостей

```text
pip install -r requirements.txt
````

## Запуск программы

```text
python main.py
```

## Запуск тестов

```text
python -m pytest -v
```

## Проверка качества кода

```text
flake8 .
```

## Запуск Веб-версия

python manage.py migrate
python manage.py runserver

# Открыть http://127.0.0.1:8000/

## Git

Для проверки состояния репозитория:

```text
git status
```

## План развития

- подключение базы данных;
- реализация пользователей;
- разработка API;
- контейнеризация приложения;
- настройка CI/CD.
