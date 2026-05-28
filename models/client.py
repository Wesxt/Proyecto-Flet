import sqlite3
from core.database import get_connection

class Client:
    def __init__(self, id, fullname, doc_type, doc_num, email=None, phone=None, address=None, last_purchase=None):
        self.id = id
        self.fullname = fullname
        self.doc_type = doc_type
        self.doc_num = doc_num
        self.email = email
        self.phone = phone
        self.address = address
        self.last_purchase = last_purchase

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Client(
            id=row["id"],
            fullname=row["fullname"],
            doc_type=row["doc_type"] if "doc_type" in row.keys() else None,
            doc_num=row["doc_num"] if "doc_num" in row.keys() else None,
            email=row["email"] if "email" in row.keys() else None,
            phone=row["phone"] if "phone" in row.keys() else None,
            address=row["address"] if "address" in row.keys() else None,
            last_purchase=row["last_purchase"] if "last_purchase" in row.keys() else None
        )

    @staticmethod
    def get_all(search_term=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = '''
            SELECT c.*, MAX(s.date) as last_purchase 
            FROM clients c
            LEFT JOIN sales s ON c.id = s.client_id
            WHERE 1=1
        '''
        params = []
        if search_term:
            query += " AND (c.fullname LIKE ? OR c.doc_num LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        query += " GROUP BY c.id"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [Client.from_row(r) for r in rows]

    @staticmethod
    def get_by_doc(doc_num, doc_type):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE doc_num = ? AND doc_type = ?", (doc_num, doc_type))
        row = cursor.fetchone()
        conn.close()
        return Client.from_row(row) if row else None

    @staticmethod
    def create(fullname, doc_type, doc_num, phone=None, email=None, address=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO clients (fullname, doc_type, doc_num, phone, email, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fullname, doc_type, doc_num, phone, email, address))
            conn.commit()
            client_id = cursor.lastrowid
            return client_id
        except Exception as e:
            print(f"Error creating client: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(client_id, fullname, doc_type, doc_num, phone, email, address):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE clients SET fullname=?, doc_type=?, doc_num=?, phone=?, email=?, address=?
                WHERE id=?
            ''', (fullname, doc_type, doc_num, phone, email, address, client_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating client: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(client_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False
        finally:
            conn.close()
