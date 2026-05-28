import flet as ft
from core.colors import *
from controllers.usuarios_controller import UsuariosController

class UsuariosView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = UsuariosController(self)
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Formulario de Creación (Izquierda) ---
        self.tf_fullname = ft.TextField(label="Nombre y apellido")
        self.tf_user = ft.TextField(label="Nombre de usuario")
        self.tf_email = ft.TextField(label="E-mail")
        self.tf_pass = ft.TextField(label="Contraseña", password=True)
        self.tf_confirm = ft.TextField(label="Confirmar contraseña", password=True)
        self.tf_salary = ft.TextField(label="Salario", value="0.0")
        self.dd_role = ft.Dropdown(
            label="Rol",
            options=[
                ft.dropdown.Option("Administrador"), 
                ft.dropdown.Option("Cajero"), 
                ft.dropdown.Option("Supervisor")
            ]
        )
        self.sw_status = ft.Switch(label="Estado", value=True, active_color=SUCCESS_COLOR)

        # --- Tabla de Usuarios (Derecha) ---
        self.search_bar = ft.TextField(
            hint_text="Buscar por ID o Nombre...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            expand=True,
            on_change=lambda e: self.load_data()
        )
        self.tf_min_salary = ft.TextField(
            hint_text="Salario Mín.",
            width=120,
            bgcolor=SURFACE_COLOR,
            on_change=lambda e: self.load_data()
        )
        self.tf_max_salary = ft.TextField(
            hint_text="Salario Máx.",
            width=120,
            bgcolor=SURFACE_COLOR,
            on_change=lambda e: self.load_data()
        )
        
        search_row = ft.Row([self.search_bar, self.tf_min_salary, self.tf_max_salary], spacing=10)
        
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("ID")),
                ft.DataColumn(label=ft.Text("Nombre")), 
                ft.DataColumn(label=ft.Text("Usuario")),
                ft.DataColumn(label=ft.Text("Rol")), 
                ft.DataColumn(label=ft.Text("Salario")),
                ft.DataColumn(label=ft.Text("Estado")), 
                ft.DataColumn(label=ft.Text("Acciones"))
            ],
            rows=[],
            expand=True
        )

        left_panel = ft.Container(
            expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
            content=ft.Column([
                ft.Text("Crear usuario", weight=ft.FontWeight.BOLD, size=18),
                self.tf_fullname, self.tf_user, self.tf_email, self.tf_pass, self.tf_confirm, self.tf_salary, self.dd_role, self.sw_status,
                ft.Row([
                    ft.OutlinedButton("Restablecer", expand=True, on_click=self.reset_fields),
                    ft.Button("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=self.register_user)
                ], spacing=10)
            ], scroll=ft.ScrollMode.AUTO)
        )

        right_panel = ft.Column([
            ft.Text("Usuarios (Empleados)", weight=ft.FontWeight.BOLD, size=20),
            search_row,
            ft.Container(
                ft.Column([self.table], scroll=ft.ScrollMode.AUTO), 
                bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True
            )
        ], expand=6)

        self.content = ft.Row([left_panel, right_panel], spacing=20)

    def load_data(self):
        users = self.controller.get_users(
            self.search_bar.value, self.tf_min_salary.value, self.tf_max_salary.value
        )
        self.table.rows.clear()
        
        for user in users:
            status_icon = ft.Icons.CHECK_CIRCLE if user.status == 1 else ft.Icons.CANCEL
            status_color = SUCCESS_COLOR if user.status == 1 else DANGER_COLOR
            salary_val = user.salary
            
            self.table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(user.id))),
                    ft.DataCell(ft.Text(user.fullname)), 
                    ft.DataCell(ft.Text(user.username)),
                    ft.DataCell(ft.Text(user.role)), 
                    ft.DataCell(ft.Text(f"${salary_val:,.2f}")),
                    ft.DataCell(ft.Icon(status_icon, color=status_color)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR, on_click=lambda e, uid=user.id: self.confirm_delete_user(uid)),
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, on_click=lambda e, u=user: self.open_editor_modal(u))
                    ]))
                ])
            )
        self.page_ref.update()

    def show_toast(self, text, color):
        self.page_ref.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.snack_bar.open = True
        self.page_ref.update()

    def confirm_delete_user(self, user_id):
        def perform_delete(e):
            success, message = self.controller.delete_user(user_id)
            self.page_ref.pop_dialog()
            self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
            if success:
                self.load_data()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar", weight=ft.FontWeight.BOLD),
            content=ft.Text("¿Está seguro de que desea eliminar este empleado? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page_ref.pop_dialog() or self.page_ref.update()),
                ft.ElevatedButton("Eliminar", bgcolor=DANGER_COLOR, color="white", on_click=perform_delete)
            ],
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def register_user(self, e):
        success, message = self.controller.register_user(
            self.tf_fullname.value, self.tf_user.value, self.tf_email.value,
            self.tf_pass.value, self.tf_confirm.value, self.tf_salary.value,
            self.dd_role.value, self.sw_status.value
        )
        self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
        if success:
            self.reset_fields()
            self.load_data()

    def open_editor_modal(self, user):
        edit_fullname = ft.TextField(label="Nombre y apellido", value=user.fullname)
        edit_user = ft.TextField(label="Nombre de usuario", value=user.username)
        edit_email = ft.TextField(label="E-mail", value=user.email if user.email else "")
        edit_salary = ft.TextField(label="Salario", value=str(user.salary))
        edit_role = ft.Dropdown(
            label="Rol", 
            value=user.role, 
            options=[
                ft.dropdown.Option("Administrador"), 
                ft.dropdown.Option("Cajero"), 
                ft.dropdown.Option("Supervisor")
            ]
        )
        edit_status = ft.Switch(value=True if user.status == 1 else False, active_color=SUCCESS_COLOR)

        def save_edit(e):
            success, message = self.controller.update_user(
                user.id, edit_fullname.value, edit_user.value, edit_email.value,
                edit_salary.value, edit_role.value, edit_status.value
            )
            self.page_ref.pop_dialog()
            self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
            if success:
                self.load_data()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar usuario", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                edit_fullname, edit_user, edit_email, edit_salary, edit_role,
                ft.Row([ft.Text("Estado"), edit_status]),
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page_ref.pop_dialog() or self.page_ref.update()),
                ft.ElevatedButton("Guardar", bgcolor=PRIMARY_COLOR, color="white", on_click=save_edit)
            ],
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def reset_fields(self, e=None):
        self.tf_fullname.value = ""
        self.tf_user.value = ""
        self.tf_email.value = ""
        self.tf_pass.value = ""
        self.tf_confirm.value = ""
        self.tf_salary.value = "0.0"
        self.dd_role.value = None
        self.sw_status.value = True
        self.page_ref.update()
