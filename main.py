"""Точка входа приложения «Учёт остатков товаров на складе» (уровень ПР3).

Данные представлены объектами классов Product и StockOperation.
Поведение — методами объектов и сервисными функциями.
"""

from models.product import Product
from models.operation import StockOperation, RECEIPT, ISSUE

from services import (
    add_product,
    find_product,
    find_product_by_id,
    filter_low_stock,
    sort_products_by_stock,
    generate_warehouse_report,
    create_operation,
    cancel_operation,
)

from storage import load_operations, load_products, save_operations, save_products
from utils import input_date, input_float, input_int, input_nonempty_str

WAREHOUSE_NAME = "Центральный склад"
PRODUCTS_FILE = "data/products.json"
OPERATIONS_FILE = "data/operations.json"


def scenario_show_products(products: list[Product]) -> None:
    """Вывести список всех товаров."""
    if not products:
        print("Список товаров пуст.")
        return
    for product in products:
        print(product)


def scenario_find_product(products: list[Product]) -> None:
    """Найти товары по названию или артикулу."""
    query = input_nonempty_str("Введите название или артикул: ")
    found = find_product(products, query)
    if found:
        for product in found:
            print(f"[{product.id}] {product.name} — {product.stock} {product.unit}")
    else:
        print("Ничего не найдено.")


def scenario_low_stock(products: list[Product]) -> None:
    """Показать товары с остатком ниже порога."""
    threshold = input_int("Порог остатка (шт.): ")
    low_stock = filter_low_stock(products, threshold)
    if low_stock:
        for product in low_stock:
            print(f"[{product.id}] {product.name}: {product.stock} {product.unit}")
    else:
        print("Товаров с низким остатком нет.")


def scenario_sort_products(products: list[Product]) -> None:
    """Показать товары, отсортированные по остатку."""
    for product in sort_products_by_stock(products):
        print(f"[{product.id}] {product.name}: {product.stock} {product.unit}")


def scenario_add_product(products: list[Product]) -> None:
    """Создать новый товар и добавить его в коллекцию."""
    name = input_nonempty_str("Название товара: ")
    article = input_nonempty_str("Артикул: ")
    category = input_nonempty_str("Категория: ")
    unit = input_nonempty_str("Единица измерения (шт., кг и т.п.): ")
    price = input_float("Цена за единицу: ")
    product = add_product(products, name, article, category, unit, price)
    print(f"Товар добавлен с id {product.id}.")


def scenario_product_info(products: list[Product]) -> None:
    """Показать подробную информацию о товаре."""
    product_id = input_int("ID товара: ")
    product = find_product_by_id(products, product_id)
    if product is None:
        print("Товар с таким ID не найден.")
        return

    info = product.get_info()
    print(f"Название: {info['name']}")
    print(f"Артикул: {info['article']}")
    print(f"Остаток: {info['stock']} шт.")
    print(f"Цена: {info['price']:.2f} руб.")
    print(f"Общая стоимость: {info['total_value']:.2f} руб.")
    print(f"Статус: {info['status']}")


def scenario_check_availability(products: list[Product]) -> None:
    """Проверить, доступно ли нужное количество товара."""
    product_id = input_int("ID товара: ")
    quantity = input_int("Требуемое количество: ")
    product = find_product_by_id(products, product_id)
    if product is None:
        print("Товар с таким ID не найден.")
        return
    _, message = product.check_availability(quantity)
    print(message)


def scenario_new_operation(
    operations: list[StockOperation],
    products: list[Product],
    operation_type: str,
) -> None:
    """Создать операцию прихода или расхода товара."""
    action = "Приход" if operation_type == RECEIPT else "Расход"
    product_id = input_int(f"{action}: ID товара: ")
    product = find_product_by_id(products, product_id)

    if product is None:
        print("Товар с таким ID не найден.")
        return

    quantity = input_int(f"Количество ({product.unit}): ")
    operation_date = input_date("Дата операции (ДД.ММ.ГГГГ): ")
    comment = input("Комментарий (необязательно): ")

    operation = create_operation(
        operations, product, operation_type, quantity, operation_date, comment
    )
    if operation is None:
        print("Операция не выполнена: некорректное количество или недостаточно товара.")
        return

    print(f"Операция №{operation.id} создана.")
    print(
        f"Текущий остаток «{product.name}»: "
        f"{product.stock} {product.unit}"
    )


def scenario_cancel_operation(
    operations: list[StockOperation], products: list[Product]
) -> None:
    """Отменить ранее созданную операцию."""
    operation_id = input_int("ID операции для отмены: ")
    if cancel_operation(operations, operation_id):
        print("Операция отменена, остаток товара восстановлен.")
    else:
        print("Операция не найдена, уже отменена или товар отсутствует.")


def scenario_show_operations(operations: list[StockOperation]) -> None:
    """Показать историю всех операций."""
    if not operations:
        print("Операций пока нет.")
        return
    for operation in operations:
        print(operation)


def scenario_report(products: list[Product]) -> None:
    """Сформировать и вывести отчёт по складу."""
    report = generate_warehouse_report(products, WAREHOUSE_NAME)
    print(f"Склад: {report['warehouse']}")
    print(f"Товаров на складе: {report['products_count']}")
    print(f"Общая стоимость остатков: {report['total_value']:.2f} руб.")
    if report["low_stock_items"]:
        print("Товары с низким остатком: " + ", ".join(report["low_stock_items"]))
    else:
        print("Товаров с низким остатком нет.")


MENU_TEXT = """
=== Учёт остатков товаров на складе ===
1. Показать все товары
2. Найти товар (по названию/артикулу)
3. Товары с низким остатком
4. Отсортировать товары по остатку
5. Добавить новый товар
6. Информация о товаре
7. Проверить доступность количества
8. Приход товара
9. Расход товара
10. Отменить операцию
11. История операций
12. Отчёт по складу
0. Выход
"""


def main() -> None:
    """Точка запуска приложения: загрузка данных, меню, сохранение данных."""
    products = load_products(PRODUCTS_FILE)
    products_by_id = {p.id: p for p in products}
    operations = load_operations(OPERATIONS_FILE, products_by_id)

    while True:
        print(MENU_TEXT)
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                scenario_show_products(products)
            elif choice == "2":
                scenario_find_product(products)
            elif choice == "3":
                scenario_low_stock(products)
            elif choice == "4":
                scenario_sort_products(products)
            elif choice == "5":
                scenario_add_product(products)
            elif choice == "6":
                scenario_product_info(products)
            elif choice == "7":
                scenario_check_availability(products)
            elif choice == "8":
                scenario_new_operation(operations, products, RECEIPT)
            elif choice == "9":
                scenario_new_operation(operations, products, ISSUE)
            elif choice == "10":
                scenario_cancel_operation(operations, products)
            elif choice == "11":
                scenario_show_operations(operations)
            elif choice == "12":
                scenario_report(products)
            elif choice == "0":
                save_products(PRODUCTS_FILE, products)
                save_operations(OPERATIONS_FILE, operations)
                print("Данные сохранены. До свидания!")
                break
            else:
                print("Неизвестный пункт меню, попробуйте снова.")
        except KeyError as error:
            print(f"Ошибка данных: не найден ключ {error}.")
        except ValueError as error:
            print(f"Ошибка ввода данных: {error}")


if __name__ == "__main__":
    main()