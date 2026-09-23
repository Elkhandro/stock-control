from datetime import datetime, date

# Простые типы данных для начального состояния склада
warehouse_name = "Центральный склад"
products = {
    "Ноутбук Lenovo": {"article": "NB-001", "stock": 15, "price": 75000.50},
    "Монитор Samsung": {"article": "MN-002", "stock": 8, "price": 25000.00},
    "Клавиатура Logitech": {"article": "KB-003", "stock": 25, "price": 3500.00}
}

# Функция 1: Проверка наличия товара
def check_availability(product_name, quantity=1):
    """
    Проверяет, достаточно ли товара на складе
    """
    if product_name in products:
        if products[product_name]["stock"] >= quantity:
            return True, "Товар доступен"
        return False, f"Недостаточно товара. Остаток: {products[product_name]['stock']} шт."
    return False, "Товар не найден на складе"

# Функция 2: Приемка товара (приход)
def receive_product(product_name, quantity):
    """
    Увеличивает остаток товара на складе
    """
    if product_name not in products:
        return False, "Товар не найден на складе"
    
    if quantity <= 0:
        return False, "Количество должно быть положительным числом"
    
    products[product_name]["stock"] += quantity
    return True, f"Принято: +{quantity} шт. Новый остаток: {products[product_name]['stock']} шт."

# Функция 3: Отгрузка товара (расход)
def ship_product(product_name, quantity):
    """
    Уменьшает остаток товара при отгрузке
    """
    available, message = check_availability(product_name, quantity)
    
    if not available:
        return False, message
    
    products[product_name]["stock"] -= quantity
    return True, f"Отгружено: -{quantity} шт. Новый остаток: {products[product_name]['stock']} шт."

# Функция 4: Получение информации о товаре
def get_product_info(product_name):
    """
    Возвращает полную информацию о товаре
    """
    if product_name in products:
        product = products[product_name]
        total_value = product["stock"] * product["price"]
        return {
            "name": product_name,
            "article": product["article"],
            "stock": product["stock"],
            "price": product["price"],
            "total_value": total_value,
            "status": check_availability(product_name)[1]
        }
    return None

# Функция 5: Генерация отчета по складу
def generate_warehouse_report():
    """
    Создает отчет по всем товарам на складе
    """
    report = []
    total_warehouse_value = 0
    low_stock_items = []
    
    for product_name, data in products.items():
        total_value = data["stock"] * data["price"]
        total_warehouse_value += total_value
        status = check_availability(product_name)
        
        report.append({
            "name": product_name,
            "article": data["article"],
            "stock": data["stock"],
            "price": data["price"],
            "total_value": total_value,
            "status": status[1]
        })
        
        # Товары с низким остатком (меньше 10 штук)
        if data["stock"] < 10:
            low_stock_items.append(product_name)
    
    return {
        "warehouse": warehouse_name,
        "report_date": date.today(),
        "items": report,
        "total_value": total_warehouse_value,
        "low_stock_items": low_stock_items
    }

# Демонстрация работы функций
def main():
    print("=== Система учёта остатков товаров ===")
    print(f"Склад: {warehouse_name}")
    print(f"Дата: {date.today()}\n")
    
    # Демонстрация проверки наличия
    print("--- Проверка наличия товара ---")
    status, message = check_availability("Ноутбук Lenovo", 5)
    print(f"Ноутбук Lenovo (5 шт.): {message}")
    
    status, message = check_availability("Монитор Samsung", 100)
    print(f"Монитор Samsung (100 шт.): {message}")
    
    # Демонстрация приемки товара
    print("\n--- Приемка товара ---")
    success, message = receive_product("Клавиатура Logitech", 10)
    print(f"Клавиатура Logitech: {message}")
    
    success, message = receive_product("Неизвестный товар", 5)
    print(f"Неизвестный товар: {message}")
    
    # Демонстрация отгрузки товара
    print("\n--- Отгрузка товара ---")
    success, message = ship_product("Ноутбук Lenovo", 3)
    print(f"Ноутбук Lenovo: {message}")
    
    success, message = ship_product("Монитор Samsung", 50)
    print(f"Монитор Samsung: {message}")
    
    # Демонстрация получения информации о товаре
    print("\n--- Информация о товаре ---")
    product_info = get_product_info("Ноутбук Lenovo")
    if product_info:
        print(f"Название: {product_info['name']}")
        print(f"Артикул: {product_info['article']}")
        print(f"Остаток: {product_info['stock']} шт.")
        print(f"Цена: {product_info['price']} руб.")
        print(f"Общая стоимость: {product_info['total_value']:.2f} руб.")
        print(f"Статус: {product_info['status']}")
    
    # Демонстрация генерации отчета
    print("\n--- Отчет по складу ---")
    report = generate_warehouse_report()
    print(f"Склад: {report['warehouse']}")
    print(f"Дата отчета: {report['report_date']}")
    print(f"Общая стоимость товаров: {report['total_value']:.2f} руб.")
    print("\nТовары:")
    for item in report['items']:
        print(f"  {item['name']} (арт. {item['article']}): {item['stock']} шт. - {item['total_value']:.2f} руб.")
    
    if report['low_stock_items']:
        print(f"\nВнимание! Товары с низким остатком: {', '.join(report['low_stock_items'])}")

if __name__ == "__main__":
    main()