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
                # Verificar stock disponible antes de restar
                cursor.execute("SELECT stock, name FROM products WHERE id = ?", (item['id'],))
                prod = cursor.fetchone()
                if not prod:
                    raise Exception(f"Producto con ID {item['id']} no encontrado")
                if prod['stock'] < 1:
                    raise Exception(f"Stock insuficiente para el producto: {prod['name']}")
                
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
            SELECT s.id, s.client_id, s.user_id, s.total, s.payment_method, datetime(s.date, 'localtime') as date, c.fullname 
            FROM sales s 
            LEFT JOIN clients c ON s.client_id = c.id 
            WHERE s.status = 1
            ORDER BY s.date DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [Sale.from_row(r) for r in rows]

    @staticmethod
    def get_today_revenue():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM sales WHERE date(date, 'localtime') = date('now', 'localtime') AND status = 1")
        val = cursor.fetchone()[0]
        conn.close()
        return val or 0.0

    @staticmethod
    def get_today_sales_count():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sales WHERE date(date, 'localtime') = date('now', 'localtime') AND status = 1")
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
            return {"total_ventas": 0, "total_efectivo": 0.0, "total_tarjeta": 0.0, "total_transferencia": 0.0, "total_esperado": 0.0}
            
        user_id = u["id"]
        
        # Today's active sales for user
        cursor.execute('''
            SELECT total, payment_method 
            FROM sales 
            WHERE user_id = ? AND date(date, 'localtime') = date('now', 'localtime') AND status = 1
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        import re
        efectivo = 0.0
        tarjeta = 0.0
        transferencia = 0.0
        total_ventas = len(rows)
        
        for r in rows:
            total = r["total"]
            metodo = r["payment_method"]
            
            if metodo == 'Efectivo':
                efectivo += total
            elif metodo == 'Tarjeta':
                tarjeta += total
            elif metodo == 'Transferencia':
                transferencia += total
            elif metodo.startswith('Pago Mixto'):
                ef = re.search(r'Efectivo:\s*([\d\.]+)', metodo)
                tj = re.search(r'Tarjeta:\s*([\d\.]+)', metodo)
                tr = re.search(r'Transferencia:\s*([\d\.]+)', metodo)
                
                efectivo += float(ef.group(1)) if ef else 0.0
                tarjeta += float(tj.group(1)) if tj else 0.0
                transferencia += float(tr.group(1)) if tr else 0.0
                
        total_esperado = efectivo + tarjeta + transferencia
        
        return {
            "total_ventas": total_ventas,
            "total_efectivo": efectivo,
            "total_tarjeta": tarjeta,
            "total_transferencia": transferencia,
            "total_esperado": total_esperado
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
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? AND s.status = 1
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
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? AND s.status = 1
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
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? AND s.status = 1
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
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? AND s.status = 1
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
            WHERE datetime(s.date, 'localtime') BETWEEN ? AND ? AND s.status = 1
            GROUP BY p.id 
            ORDER BY ganancia DESC
        ''', (st, ed))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_sales_for_client(client_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, datetime(s.date, 'localtime') as date, s.total, s.payment_method, u.fullname as cajero
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE s.client_id = ? AND s.status = 1
            ORDER BY s.date DESC
        ''', (client_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def void_sale(sale_id, username):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            # Check current status
            cursor.execute("SELECT status, total, client_id, user_id FROM sales WHERE id = ?", (sale_id,))
            sale = cursor.fetchone()
            if not sale:
                raise Exception("Venta no encontrada")
            if sale["status"] == 0:
                raise Exception("La venta ya está anulada")
                
            # Update sale status
            cursor.execute("UPDATE sales SET status = 0 WHERE id = ?", (sale_id,))
            
            # Get sale details to restore stock
            cursor.execute("SELECT product_id, quantity FROM sale_details WHERE sale_id = ?", (sale_id,))
            details = cursor.fetchall()
            for d in details:
                cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (d["quantity"], d["product_id"]))
                
            conn.commit()
            
            # Log audit event
            from models.audit import AuditEvent
            from models.user import User
            import datetime
            user = User.get_by_username(username)
            user_role = user.role if user else "Cajero"
            
            client_name = "Consumidor Final"
            if sale["client_id"]:
                cursor.execute("SELECT fullname FROM clients WHERE id = ?", (sale["client_id"],))
                client_row = cursor.fetchone()
                if client_row:
                    client_name = client_row["fullname"]
            
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            AuditEvent.log_event("Anulación de Factura", {
                "factura": str(sale_id),
                "fecha_exacta": now_str,
                "cliente": client_name,
                "usuario": username,
                "rol": user_role,
                "total": f"{sale['total']:.2f}"
            })
            return True, "Venta anulada con éxito y stock restaurado"
        except Exception as e:
            conn.rollback()
            print(f"Error voiding sale: {e}")
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def get_all_sales_list():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, datetime(s.date, 'localtime') as date, s.total, s.payment_method, s.status,
                   u.fullname as cajero, c.fullname as cliente, c.doc_num as cliente_doc
            FROM sales s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN clients c ON s.client_id = c.id
            ORDER BY s.date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_sale_details(sale_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sd.quantity, sd.price, p.name as product_name, p.codigo_producto
            FROM sale_details sd
            JOIN products p ON sd.product_id = p.id
            WHERE sd.sale_id = ?
        ''', (sale_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
