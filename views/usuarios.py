import flet as ft
from core.colors import *

def UsuariosView(page: ft.Page):
    """
    Administración de Usuarios (Imagen 15).
    Panel izquierdo de creación, derecho de visualización con buscador.
    """
    
    # --- Formulario de Creación (Izquierda) ---
    tf_fullname = ft.TextField(label="Nombre y apellido")
    tf_user = ft.TextField(label="Nombre de usuario")
    tf_email = ft.TextField(label="E-mail")
    tf_pass = ft.TextField(label="Contraseña", password=True)
    tf_confirm = ft.TextField(label="Confirmar contraseña", password=True)
    dd_role = ft.Dropdown(
        label="Rol",
        options=[ft.dropdown.Option("Administrador"), ft.dropdown.Option("Cajero"), ft.dropdown.Option("Supervisor")]
    )
    sw_status = ft.Switch(label="Estado", value=True, active_color=SUCCESS_COLOR)

    def open_editor_modal(e):
        # Ventana emergente "Editor usuario" (Imagen 15)
        dialog = ft.AlertDialog(
            title=ft.Text("Editor usuario", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.TextField(label="Nombre y apellido", value="Admin Principal"),
                ft.TextField(label="Nombre de usuario", value="admin_1"),
                ft.TextField(label="E-mail", value="admin@empresa.com"),
                ft.TextField(label="Contraseña", value="******", password=True),
                ft.TextField(label="Confirmar contraseña", value="******", password=True),
                ft.Dropdown(label="Rol", value="Administrador", options=[ft.dropdown.Option("Administrador")]),
                ft.Row([ft.Text("Estado"), ft.Switch(value=True, active_color=SUCCESS_COLOR)]),
                ft.ElevatedButton("Editar", bgcolor=PRIMARY_COLOR, color="white", width=400)
            ], tight=True, spacing=15),
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Tabla de Usuarios (Derecha) ---
    search_bar = ft.TextField(hint_text="Buscar Usuarios...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nombre")), ft.DataColumn(label=ft.Text("Usuario")),
            ft.DataColumn(label=ft.Text("Rol")), ft.DataColumn(label=ft.Text("Estado")), ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Admin Principal")), ft.DataCell(ft.Text("admin_1")),
                ft.DataCell(ft.Text("Administrador")), ft.DataCell(ft.Icon(ft.Icons.CHECK_CIRCLE, color=SUCCESS_COLOR)),
                ft.DataCell(ft.Row([ft.IconButton(ft.Icons.DELETE_OUTLINE), ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=open_editor_modal)]))
            ])
        ],
        expand=True
    )

    # --- Layout ---
    left_panel = ft.Container(
        expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Text("Crear usuario", weight=ft.FontWeight.BOLD, size=18),
            tf_fullname, tf_user, tf_email, tf_pass, tf_confirm, dd_role, sw_status,
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True),
                ft.ElevatedButton("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    right_panel = ft.Column([
        ft.Text("Usuarios", weight=ft.FontWeight.BOLD, size=20),
        search_bar,
        ft.Container(table, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
    ], expand=6)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([left_panel, right_panel], spacing=20)
    )
