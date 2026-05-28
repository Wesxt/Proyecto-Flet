from models.cash_register import CashRegister
from models.product import Product
from models.sale import Sale

class POSController:
    def __init__(self, view):
        self.view = view

    def check_active_register(self, username):
        register = CashRegister.get_active_register(username)
        if register:
            return register
        return None

    def open_cash_register(self, username, initial_amount):
        return CashRegister.open_register(username, initial_amount)

    def get_register_close_data(self, active_register):
        # We need the username and stats
        # active_register is a CashRegister object
        # We need opening_time and user_id to compute sales since opening
        import sqlite3
        from core.database import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN payment_method = 'Efectivo' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN payment_method = 'Tarjeta' THEN total ELSE 0 END) as total_tarjeta,
                SUM(total) as total_ventas
            FROM sales 
            WHERE user_id = ? AND date >= ?
        ''', (active_register.user_id, active_register.opening_time))
        res = cursor.fetchone()
        conn.close()
        
        efectivo = res["total_efectivo"] or 0
        tarjeta = res["total_tarjeta"] or 0
        esperado = active_register.initial_amount + efectivo
        
        return {
            "efectivo": efectivo,
            "tarjeta": tarjeta,
            "esperado": esperado
        }

    def close_cash_register(self, register_id, expected_amount, actual_amount, cash_sales, card_sales, difference):
        return CashRegister.close_register(register_id, expected_amount, actual_amount, cash_sales, card_sales, difference)

    def get_active_products(self):
        return Product.get_active()

    def add_item_to_cart(self, state, prod_id, name, price):
        item_data = {"id": prod_id, "name": name, "price": price}
        state.cart_items.append(item_data)

    def remove_item_from_cart(self, state, item_data):
        if item_data in state.cart_items:
            state.cart_items.remove(item_data)

    def clear_cart(self, state):
        state.cart_items.clear()
