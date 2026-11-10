-- Схема базы данных склада (ПР7)

-- Таблица товаров
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    article TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'шт.',
    price REAL NOT NULL DEFAULT 0,
    stock INTEGER NOT NULL DEFAULT 0
);

-- Таблица складских операций (связана с товарами через product_id)
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL CHECK (operation_type IN ('приход', 'расход')),
    quantity INTEGER NOT NULL,
    operation_date TEXT NOT NULL,
    comment TEXT,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Индекс для ускорения поиска операций по товару
CREATE INDEX IF NOT EXISTS idx_operations_product_id ON operations(product_id);