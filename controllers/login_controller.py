from models.user import User
from models.audit import AuditEvent
import datetime

class LoginController:
    def __init__(self, view, on_login_success):
        self.view = view
        self.on_login_success = on_login_success

    def do_login(self, username, password):
        if not username or not password:
            self.view.show_error("Por favor, ingrese usuario y contraseña")
            return

        user = User.get_by_username_and_password(username, password)
        if user:
            # Actualizar marca de tiempo de último acceso
            User.update_last_access(user.id)
            
            # Registrar auditoría de inicio de sesión exitoso
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            AuditEvent.log_event("Inicio de Sesión", {
                "usuario": user.username,
                "fecha_exacta": now_str,
                "rol": user.role
            })
            self.on_login_success(user.role, user.username)
        else:
            self.view.show_error("Usuario o contraseña incorrectos")

    def send_recovery_verification(self, email, new_pass, confirm_pass):
        if not email or not new_pass or not confirm_pass:
            pass
        self.view.show_recovery_info()
