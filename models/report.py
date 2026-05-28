import sqlite3
from core.database import get_connection

class Report:
    def __init__(self, id, r_type, start_date, end_date, summary, created_at):
        self.id = id
        self.type = r_type
        self.start_date = start_date
        self.end_date = end_date
        self.summary = summary
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if not row:
            return None
        return Report(
            id=row["id"],
            r_type=row["type"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            summary=row["summary"],
            created_at=row["created_at"]
        )

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [Report.from_row(r) for r in rows]

    @staticmethod
    def get_by_id(report_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        row = cursor.fetchone()
        conn.close()
        return Report.from_row(row)

    @staticmethod
    def create(r_type, start_date, end_date, summary):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO reports (type, start_date, end_date, summary)
                VALUES (?, ?, ?, ?)
            ''', (r_type, start_date, end_date, summary))
            conn.commit()
            report_id = cursor.lastrowid
            return report_id
        except Exception as e:
            print(f"Error creating report: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def delete(report_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting report: {e}")
            return False
        finally:
            conn.close()
