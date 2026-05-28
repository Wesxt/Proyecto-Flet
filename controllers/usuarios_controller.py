from models.user import User

class UsuariosController:
    def __init__(self, view):
        self.view = view

    def get_users(self, search_query=None, min_salary=None, max_salary=None):
        return User.get_all(search_query, min_salary, max_salary)

    def register_user(self, fullname, username, email, password, confirm_password, salary, role, status):
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"

        if not all([fullname, username, password, role]):
            return False, "Todos los campos obligatorios"
            
        try:
            salary_val = float(salary) if salary else 0.0
        except ValueError:
            return False, "El salario debe ser un número"

        success = User.create(fullname, username, email, password, role, salary_val, 1 if status else 0)
        if success:
            return True, "Usuario registrado con éxito"
        return False, "Error al registrar el usuario"

    def update_user(self, user_id, fullname, username, email, salary, role, status):
        try:
            new_salary = float(salary) if salary else 0.0
        except ValueError:
            return False, "El salario debe ser un número válido"
            
        success = User.update(user_id, fullname, username, email, role, new_salary, 1 if status else 0)
        if success:
            return True, "Usuario actualizado exitosamente"
        return False, "Error al actualizar el usuario"

    def delete_user(self, user_id):
        success = User.delete(user_id)
        if success:
            return True, "Usuario eliminado con éxito"
        return False, "Error al eliminar el usuario"
