import flet as ft
from core.colors import *

def ProductosView(page: ft.Page):
    """
    Catálogo y Detalle de Productos (Imagen 10).
    Incluye ID/Código autogenerados, gestión visual y cambio de estado.
    """
    
    # --- Formulario de Creación ---
    tf_name = ft.TextField(label="Nombre")
    tf_desc = ft.TextField(label="Descripción", multiline=True, min_lines=2)
    tf_price_buy = ft.TextField(label="Precio de compra", expand=True)
    tf_price_sell = ft.TextField(label="Precio de venta", expand=True)
    tf_stock_actual = ft.TextField(label="Stock actual", expand=True)
    tf_stock_min = ft.TextField(label="Stock mínimo", expand=True)
    dd_category = ft.Dropdown(label="Categoría", options=[ft.dropdown.Option("Alimentos"), ft.dropdown.Option("Bebidas")], expand=True)
    
    sw_status = ft.Switch(label="Estado (On/Off)", value=True, active_color=SUCCESS_COLOR)

    def open_product_detail(e):
        # Ventana de "Info producto" (Imagen 10)
        dialog = ft.AlertDialog(
            title=ft.Text("Info producto", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.TextField(label="Nombre", value="Producto X"),
                ft.TextField(label="Descripción", value="Descripción del producto..."),
                ft.TextField(label="Precio de compra", value="5000"),
                ft.TextField(label="Precio de venta", value="7500"),
                ft.TextField(label="Stock", value="100"),
                ft.TextField(label="Stock mínimo", value="10"),
                ft.TextField(label="Categoría", value="Alimentos"),
                ft.Row([ft.Text("Estado"), ft.Switch(value=True, active_color=SUCCESS_COLOR)]),
                ft.ElevatedButton("Subir Imagen", icon=ft.Icons.UPLOAD_FILE, bgcolor=PRIMARY_COLOR, color="white"),
                ft.ElevatedButton("Editar producto", bgcolor=SECONDARY_COLOR, color="white", width=400)
            ], tight=True, scroll=ft.ScrollMode.AUTO, spacing=15),
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Lista de Productos ---
    search_bar = ft.TextField(hint_text="Buscar Producto...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    
    product_grid = ft.Row(
        wrap=True, spacing=15, run_spacing=15,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.IMAGE, size=40, color=TEXT_SECONDARY),
                    ft.Text("Producto X", weight=ft.FontWeight.BOLD),
                    ft.Text("Precio: 7500", size=12, color=SUCCESS_COLOR)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=120, height=140, bgcolor=SURFACE_COLOR, border_radius=10,
                padding=10, on_click=open_product_detail, ink=True
            )
        ]
    )

    # --- Layout ---
    create_form = ft.Container(
        expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Text("Crear producto", weight=ft.FontWeight.BOLD, size=18),
            tf_name,
            tf_desc,
            ft.Row([tf_price_buy, tf_price_sell]),
            ft.Row([tf_stock_actual, tf_stock_min]),
            dd_category,
            ft.Row([sw_status, ft.ElevatedButton("Subir Imagen", icon=ft.Icons.IMAGE_OUTLINED)]),
            ft.Text("El id del producto y el código se generan automáticamente", size=11, color=PRIMARY_COLOR, italic=True),
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True),
                ft.ElevatedButton("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    list_panel = ft.Column([
        ft.Text("Productos", weight=ft.FontWeight.BOLD, size=20),
        search_bar,
        ft.Container(product_grid, expand=True, padding=10)
    ], expand=6)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([create_form, list_panel], spacing=20)
    )
