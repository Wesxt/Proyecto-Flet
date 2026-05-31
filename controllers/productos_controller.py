from models.product import Product
from models.audit import AuditEvent
from core.database import get_connection

class ProductosController:
    def __init__(self, view):
        self.view = view

    def get_products(self, search_term=None):
        return Product.get_all(search_term)

    def register_product(self, name, description, price_buy, price_sell, stock, stock_min, category, codigo_producto, status):
        if not name or price_sell is None or price_sell == "" or not codigo_producto:
            return False, "El nombre, código de producto y precio de venta son obligatorios"
        
        try:
            p_buy = float(price_buy or 0)
            p_sell = float(price_sell)
            st = float(stock or 0)
            st_min = float(stock_min or 0)
        except ValueError:
            return False, "Los precios y el stock deben ser números válidos"
            
        if p_sell <= p_buy:
            return False, "El precio de venta debe ser mayor que el precio de compra"
            
        existing = Product.get_by_code(codigo_producto)
        if existing:
            return False, "Ya existe un producto registrado con ese código"
            
        success = Product.create(name, description, p_buy, p_sell, st, st_min, category, codigo_producto, 1 if status else 0)
        if success:
            # Registrar auditoría de nuevo producto
            AuditEvent.log_event("Cambio de Producto", {
                "nombre": name,
                "codigo": codigo_producto,
                "tipo": "venta",
                "antiguo_precio": "0",
                "nuevo_precio": str(p_sell)
            })
            return True, "Producto registrado con éxito"
        return False, "Error al registrar el producto"

    def update_product(self, product_id, name, description, price_buy, price_sell, stock, stock_min, category, codigo_producto, status):
        if not name or price_sell is None or price_sell == "" or not codigo_producto:
            return False, "Nombre, código de producto y precio de venta son obligatorios"
            
        try:
            p_buy = float(price_buy or 0)
            p_sell = float(price_sell)
            st = float(stock or 0)
            st_min = float(stock_min or 0)
        except ValueError:
            return False, "Los precios y el stock deben ser números válidos"
            
        if p_sell <= p_buy:
            return False, "El precio de venta debe ser mayor que el precio de compra"
            
        existing = Product.get_by_code(codigo_producto)
        if existing and existing.id != product_id:
            return False, "Ya existe otro producto registrado con ese código"
            
        # Consultar precio antiguo antes de actualizar
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT price_sell FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        old_price = row["price_sell"] if row else 0.0
        conn.close()

        success = Product.update(product_id, name, description, p_buy, p_sell, st, st_min, category, codigo_producto, 1 if status else 0)
        if success:
            # Registrar auditoría del cambio de producto
            AuditEvent.log_event("Cambio de Producto", {
                "nombre": name,
                "codigo": codigo_producto,
                "tipo": "venta",
                "antiguo_precio": str(old_price),
                "nuevo_precio": str(p_sell)
            })
            return True, "Producto actualizado"
        return False, "Error al actualizar el producto"

    def delete_product(self, product_id):
        # Consultar datos del producto antes de borrar
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price_sell FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()

        success = Product.delete(product_id)
        if success and row:
            # Registrar auditoría del borrado
            AuditEvent.log_event("Cambio de Producto", {
                "nombre": row["name"],
                "tipo": "venta",
                "antiguo_precio": str(row["price_sell"]),
                "nuevo_precio": "0 (Eliminado)"
            })
            return True, "Producto eliminado"
        return False, "Error al eliminar el producto"
