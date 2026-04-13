import flet as ft
from core.colors import *

def ClientesView(page: ft.Page):
    """
    Gestión de Clientes Frecuentes (Imagen 9).
    Formulario de registro y tabla con historial.
    """
    
    # --- Formulario de Registro ---
    tf_name = ft.TextField(label="Nombre y apellido", expand=True)
    dd_doc_type = ft.Dropdown(
        label="Tipo de documento",
        options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT")],
        width=200
    )
    tf_doc_num = ft.TextField(label="Número de documento", expand=True)
    tf_phone = ft.TextField(label="Teléfono (Opcional)", expand=True)
    tf_email = ft.TextField(label="E-mail (Opcional)", expand=True)
    tf_address = ft.TextField(label="Dirección (Opcional)", expand=True)

    def open_info_modal(e):
        # Ventana emergente con "Información adicional" (Imagen 9)
        dialog = ft.AlertDialog(
            title=ft.Text("Información adicional", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.TextField(label="Nombre y apellido", value="Andres", border_color=PRIMARY_COLOR),
                ft.Dropdown(label="Tipo de documento", value="Cédula de ciudadanía", options=[ft.dropdown.Option("Cédula de ciudadanía")]),
                ft.TextField(label="Número de documento", value="123456"),
                ft.TextField(label="Teléfono", value="3001234567"),
                ft.TextField(label="E-mail", value="andres@email.com"),
                ft.TextField(label="Dirección", value="Calle 123 #45-67"),
                ft.Text("Fecha de registro: 20/Sep/2026", size=12, color=TEXT_SECONDARY),
                ft.Row([ft.Text("Editor"), ft.Switch(value=False)], alignment=ft.MainAxisAlignment.END)
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Actualizar", bgcolor=PRIMARY_COLOR, color="white")
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Tabla de Clientes ---
    search_bar = ft.TextField(hint_text="Buscar cliente...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nombre")),
            ft.DataColumn(label=ft.Text("Tipo de doc")),
            ft.DataColumn(label=ft.Text("Num de doc")),
            ft.DataColumn(label=ft.Text("Última compra")),
            ft.DataColumn(label=ft.Text("Acciones")),
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Andres")),
                ft.DataCell(ft.Text("NIT")),
                ft.DataCell(ft.Text("123456")),
                ft.DataCell(ft.Text("12/Sep/2026")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR),
                    ft.IconButton(ft.Icons.EXPAND_CIRCLE_DOWN_OUTLINED, icon_color=PRIMARY_COLOR, on_click=open_info_modal),
                ]))
            ])
        ],
        expand=True
    )

    # --- Layout ---
    registration_form = ft.Container(
        expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Text("Registrar cliente frecuente", weight=ft.FontWeight.BOLD, size=18),
            tf_name,
            ft.Row([dd_doc_type, tf_doc_num]),
            tf_phone,
            tf_email,
            tf_address,
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True),
                ft.ElevatedButton("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    data_panel = ft.Column([
        ft.Text("Clientes frecuentes", weight=ft.FontWeight.BOLD, size=20),
        search_bar,
        ft.Container(table, bgcolor=SURFACE_COLOR, border_radius=BORDER_RADIUS, padding=10, expand=True)
    ], expand=6)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([registration_form, data_panel], spacing=20)
    )
