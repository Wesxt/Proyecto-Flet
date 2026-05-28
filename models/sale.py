import sqlite3
from core.database import get_connection

class Sale:
    def __init__(self, id, client_id, user_id, total, payment_method, date, client_name=None, user_name=None):
        self.id = id
        self.client_id = client_id
        self.user_id = user_id
        self.total = total
        self.payment_method = payment_method
        self.date = date
        self.client_name = client_name
        self.user_name = user_name

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Sale(
            id=row["id"],
            client_id=row["client_id"],
            user_id=row["user_id"],
            total=row["total"],
            payment_method=row["payment_method"],
            date=row["date"],
            client_name=row["fullname"] if "fullname" in row.keys() else None,
            user_name=row["cajero"] if "cajero" in row.keys() else None
        )

    @staticmethod
    def create_sale(client_id, user_id, total, payment_method, cart_items):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert sale
            cursor.execute('''
                INSERT INTO sales (client_id, user_id, total, payment_method)
                VALUES (?, ?, ?, ?)
            ''', (client_id, user_id, total, payment_method))
            sale_id = cursor.lastrowid
            
            # Insert details and update stock
            for item in cart_items:
                cursor.execute('''
                    INSERT INTO sale_details (sale_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (sale_id, item['id'], 1, item['price']))
                
                cursor.execute('''
                    UPDATE products 
                    SET stock = stock - 1 
                    WHERE id = ?
                ''', (item['id'],))
                
            conn.commit()
            return sale_id
        except Exception as e:
            conn.rollback()
            print(f"Error creating sale: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_recent(limit=5):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, c.fullname 
            FROM sales s 
            LEFT JOIN clients c ON s.client_id = c.id 
            ORDER BY s.date DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [Sale.from_row(r) for r in rows]

    @staticmethod
    def get_today_revenue():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM sales WHERE date(date) = date('now', 'localtime')")
        val = cursor.fetchone()[0]
        conn.close()
        return val or 0.0

    @staticmethod
    def get_today_sales_count():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales WHERE date(date) = date('now', 'localtime')")
        val = cursor.fetchone()[0]
        conn.close()
        return val or 0

    @staticmethod
    def get_today_user_sales_stats(username):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        u = cursor.fetchone()
        if not u:
            conn.close()
            return {"total_ventas": 0, "total_efectivo": 0.0, "total_tarjeta": 0.0, "total_esperado": 0.0}
            
        user_id = u["id"]
        
        # Today's sales
        cursor.execute('''
            SELECT 
                COUNT(id) as total_ventas,
                SUM(CASE WHEN payment_method = 'Efectivo' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN payment_method = 'Tarjeta' THEN total ELSE 0 END) as total_tarjeta,
                SUM(total) as total_esperado
            FROM sales 
            WHERE user_id = ? AND date(date, 'localtime') = date('now', 'localtime')
        ''', (user_id,))
        res = cursor.fetchone()
        conn.close()
        
        return {
            "total_ventas": res["total_ventas"] or 0,
            "total_efectivo": res["total_efectivo"] or 0.0,
            "total_tarjeta": res["total_tarjeta"] or 0.0,
            "total_esperado": res["total_esperado"] or 0.0
        }

    # --- Query methods for report generation ---
    @staticmethod
    def get_sales_for_period(start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        st = start_date + " 00:00:00"
        ed = end_date + " 23:59:59"
        cursor.execute('''
            SELECT s.id, datetime(s.date, 'localtime') as local_date, s.total, s.payment_method, u.fullname as cajero, c.fullname as cliente
            FROM sales s 
            LEFT JOIN users u ON s.user_id = u.id 
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ?
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_sales_by_cashier(start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        st = start_date + " 00:00:00"
        ed = end_date + " 23:59:59"
        cursor.execute('''
            SELECT u.fullname, COUNT(s.id) as cant, SUM(s.total) as total
            FROM sales s JOIN users u ON s.user_id = u.id
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? 
            GROUP BY u.id 
            ORDER BY total DESC
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_sales_by_client(start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        st = start_date + " 00:00:00"
        ed = end_date + " 23:59:59"
        cursor.execute('''
            SELECT c.fullname, c.doc_num, COUNT(s.id) as cant, SUM(s.total) as total
            FROM sales s JOIN clients c ON s.client_id = c.id
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? 
            GROUP BY c.id 
            ORDER BY total DESC
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_top_selling_products(start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        st = start_date + " 00:00:00"
        ed = end_date + " 23:59:59"
        cursor.execute('''
            SELECT p.name, SUM(sd.quantity) as qty, SUM(sd.quantity * sd.price) as total
            FROM sale_details sd JOIN products p ON sd.product_id = p.id
            JOIN sales s ON sd.sale_id = s.id
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? 
            GROUP BY p.id 
            ORDER BY qty DESC
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_profits_by_product(start_date, end_date):
        conn = get_connection()
        cursor = conn.cursor()
        st = start_date + " 00:00:00"
        ed = end_date + " 23:59:59"
        cursor.execute('''
            SELECT p.name, SUM(sd.quantity) as qty, 
                   SUM(sd.quantity * p.price_buy) as costo,
                   SUM(sd.quantity * sd.price) as ingreso,
                   SUM(sd.quantity * (sd.price - p.price_buy)) as ganancia
            FROM sale_details sd 
            JOIN products p ON sd.product_id = p.id
            JOIN sales s ON sd.sale_id = s.id
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? 
            GROUP BY p.id 
            ORDER BY ganancia DESC
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows
