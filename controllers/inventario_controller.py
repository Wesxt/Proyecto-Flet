from models.product import Product
from models.audit import AuditEvent
from core.database import get_connection
import datetime

class InventarioController:
    def __init__(self, view):
        self.view = view

    def get_items(self, search_term=None):
        return Product.get_all(search_term)

    def get_alerts(self):
        return Product.get_alerts()

    def delete_item(self, product_id):
        # Primero buscar los datos antes de borrar para el log
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, stock FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        success = Product.soft_delete(product_id)
        if success and row:
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            AuditEvent.log_event("Cambio de Inventario", {
                "item": row["name"],
                "movimiento": "salida", # baja de inventario
                "fecha_exacta": now_str,
                "unidades": str(row["stock"]),
                "restante": "0"
            })
        return success

    def save_item(self, is_edit, product_id, data):
        old_stock = 0
        if is_edit:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                old_stock = row["stock"]
            conn.close()

        success = False
        if is_edit:
            success = Product.update_inventory(
                product_id, 
                data['name'], 
                data['price_buy'], 
                data['price_sell'], 
                data['stock'], 
                data['stock_min'], 
                data['in_limit'], 
                data['out_limit'], 
                data['adj_limit']
            )
        else:
            # Creation with limits
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO products (name, price_buy, price_sell, stock, stock_min, in_limit, out_limit, adj_limit, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (data['name'], data['price_buy'], data['price_sell'], data['stock'], data['stock_min'],
                      data['in_limit'], data['out_limit'], data['adj_limit']))
                conn.commit()
                success = True
            except Exception as e:
                print(f"Error creating inventory item: {e}")
                success = False
            finally:
                conn.close()

        if success:
            # Registrar auditoría de cambio de inventario
            new_stock = data['stock']
            diff = new_stock - old_stock
            if diff > 0:
                movimiento = "entrada"
                unidades = diff
            elif diff < 0:
                movimiento = "salida"
                unidades = -diff
            else:
                movimiento = "ajuste"
                unidades = 0

            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            AuditEvent.log_event("Cambio de Inventario", {
                "item": data['name'],
                "movimiento": movimiento,
                "fecha_exacta": now_str,
                "unidades": str(unidades),
                "restante": str(new_stock)
            })

        return success
