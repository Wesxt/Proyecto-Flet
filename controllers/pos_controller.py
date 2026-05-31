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
        # We need opening_time and user_id to compute sales since opening
        import sqlite3
        import re
        from core.database import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT total, payment_method 
            FROM sales 
            WHERE user_id = ? AND date >= ? AND status = 1
        ''', (active_register.user_id, active_register.opening_time))
        rows = cursor.fetchall()
        conn.close()
        
        efectivo = 0.0
        tarjeta = 0.0
        transferencia = 0.0
        
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
                
        esperado = active_register.initial_amount + efectivo
        
        return {
            "efectivo": efectivo,
            "tarjeta": tarjeta,
            "transferencia": transferencia,
            "esperado": esperado
        }

    def close_cash_register(self, register_id, expected_amount, actual_amount, cash_sales, card_sales, transfer_sales, difference):
        return CashRegister.close_register(register_id, expected_amount, actual_amount, cash_sales, card_sales, transfer_sales, difference)

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
