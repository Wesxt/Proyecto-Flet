import sqlite3
import json
import datetime
from core.database import get_connection

class AuditEvent:
    def __init__(self, id, event_type, timestamp, details):
        self.id = id
        self.event_type = event_type
        self.timestamp = timestamp
        self.details = details

    @staticmethod
    def from_row(row):
        if not row:
            return None
        
        # Formatear la fecha para mantener uniformidad (DD/MM/YYYY HH:MM)
        ts = row["timestamp"]
        try:
            if "-" in ts:
                # e.g. "2026-04-12 08:00:45" o "2026-05-28 03:28:45"
                dt = datetime.datetime.strptime(ts.split(".")[0], "%Y-%m-%d %H:%M:%S")
                ts_formatted = dt.strftime("%d/%m/%Y %H:%M")
            else:
                ts_formatted = ts
        except Exception:
            ts_formatted = ts
            
        try:
            details_dict = json.loads(row["details"])
        except Exception:
            details_dict = {}
            
        return AuditEvent(
            id=row["id"],
            event_type=row["event_type"],
            timestamp=ts_formatted,
            details=details_dict
        )

    @staticmethod
    def get_all(search_term=None):
        conn = get_connection()
        cursor = conn.cursor()
        # Ordenamos descendente por ID para tener los eventos más recientes primero
        cursor.execute("SELECT id, event_type, datetime(timestamp, 'localtime') as timestamp, details FROM audit_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        events = [AuditEvent.from_row(r) for r in rows]
        
        if search_term:
            search_term = search_term.lower()
            filtered_events = []
            for ev in events:
                match = False
                if search_term in ev.event_type.lower() or search_term in ev.timestamp.lower():
                    match = True
                else:
                    for k, v in ev.details.items():
                        if search_term in str(v).lower():
                            match = True
                            break
                if match:
                    filtered_events.append(ev)
            return filtered_events
            
        return events

    @staticmethod
    def log_event(event_type, details_dict):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO audit_logs (event_type, details)
                VALUES (?, ?)
            ''', (event_type, json.dumps(details_dict)))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging audit event: {e}")
            return False
        finally:
            conn.close()
