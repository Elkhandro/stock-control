-- ==================== ВЫБОРКА СПИСКОВ (2) ====================
-- 1. Список всех товаров, отсортированных по названию
SELECT id, name, article, category, price, stock FROM products ORDER BY name;

-- 2. История операций, последние сверху
SELECT id, product_id, operation_type, quantity, operation_date, is_cancelled 
FROM operations ORDER BY operation_date DESC, id DESC;

-- ==================== ФИЛЬТРАЦИЯ WHERE (2) ====================
-- 3. Товары с низким остатком (меньше 10 штук)
SELECT name, article, stock FROM products WHERE stock < 10;

-- 4. Активные (не отмененные) операции прихода за последний месяц (LIKE для демонстрации)
SELECT * FROM operations 
WHERE operation_type = 'приход' AND is_cancelled = 0 AND operation_date LIKE '2026-10%';

-- ==================== JOIN (2) ====================
-- 5. Операции с названиями товаров (INNER JOIN)
SELECT o.id, p.name AS product_name, o.operation_type, o.quantity, o.operation_date
FROM operations o
JOIN products p ON o.product_id = p.id
ORDER BY o.operation_date DESC;

-- 6. Товары и их последняя операция (LEFT JOIN чтобы показать товары без операций)
SELECT p.name, p.stock, o.operation_type, o.operation_date
FROM products p
LEFT JOIN operations o ON p.id = o.product_id
WHERE o.id IS NULL OR o.id = (SELECT MAX(id) FROM operations WHERE product_id = p.id);

-- ==================== АГРЕГАТНЫЕ ФУНКЦИИ (2) ====================
-- 7. Общая стоимость всех остатков на складе
SELECT SUM(price * stock) AS total_value FROM products;

-- 8. Количество активных операций по типам
SELECT operation_type, COUNT(*) AS op_count 
FROM operations WHERE is_cancelled = 0 GROUP BY operation_type;

-- ==================== ГРУППИРОВКА + HAVING (2) ====================
-- 9. Категории с общим остатком больше 20 единиц (LEFT JOIN + GROUP BY + HAVING)
SELECT p.category, SUM(p.stock) AS total_stock
FROM products p
LEFT JOIN operations o ON p.id = o.product_id
GROUP BY p.category
HAVING total_stock > 20;

-- 10. Товары, по которым было более 3 операций (GROUP BY + HAVING + COUNT)
SELECT p.name, COUNT(o.id) AS operations_count
FROM products p
JOIN operations o ON p.id = o.product_id
GROUP BY p.id, p.name
HAVING operations_count > 3;