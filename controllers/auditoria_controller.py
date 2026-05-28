from models.audit import AuditEvent

class AuditoriaController:
    def __init__(self, view):
        self.view = view

    def get_audit_events(self, search_term=None):
        return AuditEvent.get_all(search_term)
