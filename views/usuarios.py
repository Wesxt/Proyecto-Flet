import flet as ft
from core.colors import *
from core.database import get_connection

def UsuariosView(page: ft.Page):
    """
    Administración de Usuarios.
    """
    
    # --- Formulario de Creación (Izquierda) ---
    tf_fullname = ft.TextField(label="Nombre y apellido")
    tf_user = ft.TextField(label="Nombre de usuario")
    tf_email = ft.TextField(label="E-mail")
    tf_pass = ft.TextField(label="Contraseña", password=True)
    tf_confirm = ft.TextField(label="Confirmar contraseña", password=True)
    dd_role = ft.Dropdown(
        label="Rol",
        options=[
            ft.dropdown.Option("Administrador"), 
            ft.dropdown.Option("Cajero"), 
            ft.dropdown.Option("Supervisor")
        ]
    )
    sw_status = ft.Switch(label="Estado", value=True, active_color=SUCCESS_COLOR)

    # --- Tabla de Usuarios (Derecha) ---
    search_bar = ft.TextField(
        hint_text="Buscar Usuarios...", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        on_change=lambda e: load_users(e.control.value)
    )
    
    table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nombre")), 
            ft.DataColumn(label=ft.Text("Usuario")),
            ft.DataColumn(label=ft.Text("Rol")), 
            ft.DataColumn(label=ft.Text("Estado")), 
            ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[],
        expand=True
    )

    def load_users(search_query=""):
        conn = get_connection()
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT * FROM users WHERE fullname LIKE ? OR username LIKE ?", (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT * FROM users")
        
        users = cursor.fetchall()
        conn.close()

        table.rows.clear()
        for user in users:
            status_icon = ft.Icons.CHECK_CIRCLE if user["status"] == 1 else ft.Icons.CANCEL
            status_color = SUCCESS_COLOR if user["status"] == 1 else DANGER_COLOR
            
            table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(user["fullname"])), 
                    ft.DataCell(ft.Text(user["username"])),
                    ft.DataCell(ft.Text(user["role"])), 
                    ft.DataCell(ft.Icon(status_icon, color=status_color)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR, on_click=lambda e, u=user: delete_user(u["id"])),
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, on_click=lambda e, u=user: open_editor_modal(u))
                    ]))
                ])
            )
        page.update()

    def delete_user(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        load_users(search_bar.value)

    def register_user(e):
        if tf_pass.value != tf_confirm.value:
            page.snack_bar = ft.SnackBar(ft.Text("Las contraseñas no coinciden"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()
            return

        if not all([tf_fullname.value, tf_user.value, tf_pass.value, dd_role.value]):
            page.snack_bar = ft.SnackBar(ft.Text("Todos los campos obligatorios"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (fullname, username, email, password, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tf_fullname.value, tf_user.value, tf_email.value, tf_pass.value, dd_role.value, 1 if sw_status.value else 0))
            conn.commit()
            conn.close()
            
            # Limpiar campos
            tf_fullname.value = ""
            tf_user.value = ""
            tf_email.value = ""
            tf_pass.value = ""
            tf_confirm.value = ""
            dd_role.value = None
            
            page.snack_bar = ft.SnackBar(ft.Text("Usuario registrado con éxito"), bgcolor=SUCCESS_COLOR)
            page.snack_bar.open = True
            load_users(search_bar.value)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()

    def open_editor_modal(user):
        # Campos del editor
        edit_fullname = ft.TextField(label="Nombre y apellido", value=user["fullname"])
        edit_user = ft.TextField(label="Nombre de usuario", value=user["username"])
        edit_email = ft.TextField(label="E-mail", value=user["email"])
        edit_role = ft.Dropdown(
            label="Rol", 
            value=user["role"], 
            options=[
                ft.dropdown.Option("Administrador"), 
                ft.dropdown.Option("Cajero"), 
                ft.dropdown.Option("Supervisor")
            ]
        )
        edit_status = ft.Switch(value=True if user["status"] == 1 else False, active_color=SUCCESS_COLOR)

        def save_edit(e):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET fullname = ?, username = ?, email = ?, role = ?, status = ?
                WHERE id = ?
            ''', (edit_fullname.value, edit_user.value, edit_email.value, edit_role.value, 1 if edit_status.value else 0, user["id"]))
            conn.commit()
            conn.close()
            dialog.open = False
            load_users(search_bar.value)
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar usuario", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                edit_fullname, edit_user, edit_email, edit_role,
                ft.Row([ft.Text("Estado"), edit_status]),
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                ft.ElevatedButton("Guardar", bgcolor=PRIMARY_COLOR, color="white", on_click=save_edit)
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    def reset_fields(e):
        tf_fullname.value = ""
        tf_user.value = ""
        tf_email.value = ""
        tf_pass.value = ""
        tf_confirm.value = ""
        dd_role.value = None
        page.update()

    # --- Layout ---
    left_panel = ft.Container(
        expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Text("Crear usuario", weight=ft.FontWeight.BOLD, size=18),
            tf_fullname, tf_user, tf_email, tf_pass, tf_confirm, dd_role, sw_status,
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True, on_click=reset_fields),
                ft.ElevatedButton("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=register_user)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    right_panel = ft.Column([
        ft.Text("Usuarios", weight=ft.FontWeight.BOLD, size=20),
        search_bar,
        ft.Container(
            ft.Column([table], scroll=ft.ScrollMode.AUTO), 
            bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True
        )
    ], expand=6)

    # Cargar usuarios inicialmente
    load_users()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([left_panel, right_panel], spacing=20)
    )
