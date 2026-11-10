import json
import os
from db.database import get_connection

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def import_data():
    conn = get_connection()
    try:
        # Импорт товаров
        with open(os.path.join(DATA_DIR, "products.json"), "r", encoding="utf-8") as f:
            products = json.load(f)
        
        conn.executemany(
            "INSERT OR REPLACE INTO products (id, name, article, category, unit, price, stock) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(p["id"], p["name"], p["article"], p.get("category"), p["unit"], p["price"], p["stock"]) for p in products]
        )
        print(f"✅ Импортировано товаров: {len(products)}")

        # Импорт операций
        with open(os.path.join(DATA_DIR, "operations.json"), "r", encoding="utf-8") as f:
            ops = json.load(f)
        
        conn.executemany(
            "INSERT OR REPLACE INTO operations (id, product_id, operation_type, quantity, operation_date, comment, is_cancelled) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(o["id"], o["product_id"], o["operation_type"], o["quantity"], o["operation_date"], o.get("comment"), int(o.get("is_cancelled", False))) for o in ops]
        )
        print(f"✅ Импортировано операций: {len(ops)}")

        conn.commit()
        print("💾 Данные успешно сохранены в БД")

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка импорта: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    import_data()