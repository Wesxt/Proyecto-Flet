import sqlite3
from core.database import get_connection

class CashRegister:
    def __init__(self, id, user_id, opening_time, closing_time, initial_amount, expected_amount, actual_amount, cash_sales, card_sales, difference, status):
        self.id = id
        self.user_id = user_id
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.initial_amount = initial_amount
        self.expected_amount = expected_amount
        self.actual_amount = actual_amount
        self.cash_sales = cash_sales
        self.card_sales = card_sales
        self.difference = difference
        self.status = status

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return CashRegister(
            id=row["id"],
            user_id=row["user_id"],
            opening_time=row["opening_time"],
            closing_time=row["closing_time"],
            initial_amount=row["initial_amount"],
            expected_amount=row["expected_amount"],
            actual_amount=row["actual_amount"],
            cash_sales=row["cash_sales"],
            card_sales=row["card_sales"],
            difference=row["difference"],
            status=row["status"]
        )

    @staticmethod
    def get_active_register(username):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return None
            
        user_id = user["id"]
        cursor.execute("SELECT * FROM cash_registers WHERE user_id = ? AND status = 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return CashRegister.from_row(row)

    @staticmethod
    def open_register(username, initial_amount):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if not user:
                return False
            user_id = user["id"]
            
            cursor.execute('''
                INSERT INTO cash_registers (user_id, initial_amount, status)
                VALUES (?, ?, 1)
            ''', (user_id, initial_amount))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error opening cash register: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def close_register(register_id, expected_amount, actual_amount, cash_sales, card_sales, difference):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE cash_registers 
                SET closing_time = CURRENT_TIMESTAMP, 
                    expected_amount = ?, 
                    actual_amount = ?, 
                    cash_sales = ?, 
                    card_sales = ?, 
                    difference = ?, 
                    status = 0
                WHERE id = ?
            ''', (expected_amount, actual_amount, cash_sales, card_sales, difference, register_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error closing cash register: {e}")
            return False
        finally:
            conn.close()
