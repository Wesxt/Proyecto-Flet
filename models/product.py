import sqlite3
from core.database import get_connection

class Product:
    def __init__(self, id, name, description, price_buy, price_sell, stock, stock_min, category, in_limit=10, out_limit=10, adj_limit=10, status=1, image=None):
        self.id = id
        self.name = name
        self.description = description
        self.price_buy = price_buy
        self.price_sell = price_sell
        self.stock = stock
        self.stock_min = stock_min
        self.category = category
        self.in_limit = in_limit
        self.out_limit = out_limit
        self.adj_limit = adj_limit
        self.status = status
        self.image = image

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Product(
            id=row["id"],
            name=row["name"],
            description=row["description"] if "description" in row.keys() else None,
            price_buy=row["price_buy"] if "price_buy" in row.keys() else 0.0,
            price_sell=row["price_sell"],
            stock=row["stock"] if "stock" in row.keys() else 0.0,
            stock_min=row["stock_min"] if "stock_min" in row.keys() else 0.0,
            category=row["category"] if "category" in row.keys() else None,
            in_limit=row["in_limit"] if "in_limit" in row.keys() else 10,
            out_limit=row["out_limit"] if "out_limit" in row.keys() else 10,
            adj_limit=row["adj_limit"] if "adj_limit" in row.keys() else 10,
            status=row["status"] if "status" in row.keys() else 1,
            image=row["image"] if "image" in row.keys() else None
        )

    @staticmethod
    def get_all(search_term=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE status = 1"
        params = []
        if search_term:
            query += " AND (name LIKE ? OR category LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Product.from_row(r) for r in rows]

    @staticmethod
    def get_active():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE status = 1")
        rows = cursor.fetchall()
        conn.close()
        return [Product.from_row(r) for r in rows]

    @staticmethod
    def get_alerts():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE status = 1 AND stock <= stock_min")
        rows = cursor.fetchall()
        conn.close()
        return [Product.from_row(r) for r in rows]

    @staticmethod
    def get_alerts_count():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= stock_min AND status = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def create(name, description, price_buy, price_sell, stock, stock_min, category, status=1):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (name, description, price_buy, price_sell, stock, stock_min, category, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, price_buy, price_sell, stock, stock_min, category, status))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating product: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(product_id, name, description, price_buy, price_sell, stock, stock_min, category, status):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE products 
                SET name=?, description=?, price_buy=?, price_sell=?, stock=?, stock_min=?, category=?, status=?
                WHERE id=?
            ''', (name, description, price_buy, price_sell, stock, stock_min, category, status, product_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_inventory(product_id, name, price_buy, price_sell, stock, stock_min, in_limit, out_limit, adj_limit):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE products 
                SET name=?, price_buy=?, price_sell=?, stock=?, stock_min=?, in_limit=?, out_limit=?, adj_limit=?
                WHERE id=?
            ''', (name, price_buy, price_sell, stock, stock_min, in_limit, out_limit, adj_limit, product_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating inventory: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def soft_delete(product_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE products SET status = 0 WHERE id = ?", (product_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error soft deleting product: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(product_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
        finally:
            conn.close()
