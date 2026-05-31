import sqlite3
from core.database import get_connection

class User:
    def __init__(self, id, fullname, username, email, password, role, salary=0.0, status=1, last_access=None, fecha_creacion=None):
        self.id = id
        self.fullname = fullname
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.salary = salary
        self.status = status
        self.last_access = last_access
        self.fecha_creacion = fecha_creacion

    @staticmethod
    def from_row(row):
        if not row:
            return None
        # Convert row keys to dict values safely (handling Row objects)
        return User(
            id=row["id"],
            fullname=row["fullname"],
            username=row["username"],
            email=row["email"],
            password=row["password"],
            role=row["role"],
            salary=row["salary"] if "salary" in row.keys() and row["salary"] is not None else 0.0,
            status=row["status"],
            last_access=row["last_access"] if "last_access" in row.keys() else None,
            fecha_creacion=row["fecha_creacion"] if "fecha_creacion" in row.keys() else None
        )

    @staticmethod
    def get_by_username_and_password(username, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND status = 1", (username,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
            
        from core.security import verify_password
        if verify_password(password, row["password"]):
            return User.from_row(row)
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return User.from_row(row)

    @staticmethod
    def get_all(search_query=None, min_salary=None, max_salary=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        if search_query:
            query += " AND (fullname LIKE ? OR id = ? OR username LIKE ?)"
            params.extend([f"%{search_query}%", search_query, f"%{search_query}%"])
        if min_salary is not None and min_salary != "":
            try:
                query += " AND salary >= ?"
                params.append(float(min_salary))
            except ValueError:
                pass
        if max_salary is not None and max_salary != "":
            try:
                query += " AND salary <= ?"
                params.append(float(max_salary))
            except ValueError:
                pass
            
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [User.from_row(r) for r in rows]

    @staticmethod
    def create(fullname, username, email, password, role, salary, status=1):
        from core.security import hash_password
        hashed_pwd = hash_password(password)
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (fullname, username, email, password, role, salary, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fullname, username, email, hashed_pwd, role, salary, status))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update(user_id, fullname, username, email, role, salary, status):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE users 
                SET fullname = ?, username = ?, email = ?, role = ?, salary = ?, status = ?
                WHERE id = ?
            ''', (fullname, username, email, role, salary, status, user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_last_access(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET last_access = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating last access: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            conn.close()
