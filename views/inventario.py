import flet as ft
from core.colors import *

def InventarioView(page: ft.Page):
    """
    Dashboard de Inventario (Imagen 11) y Edición (Imagen 12).
    Doble panel: Alertas y Items. Restricciones de movimiento.
    """
    
    # --- Alertas de Stock (Izquierda) ---
    search_alerts = ft.TextField(hint_text="Buscar Alerta por Fecha...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    table_alerts = ft.DataTable(
        columns=[ft.DataColumn(label=ft.Text("Item")), ft.DataColumn(label=ft.Text("Fecha de generado")), ft.DataColumn(label=ft.Text("Stock actual")), ft.DataColumn(label=ft.Text("Acciones"))],
        rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("Agua")), ft.DataCell(ft.Text("12/04/2026")), ft.DataCell(ft.Text("5", color=DANGER_COLOR)), ft.DataCell(ft.IconButton(ft.Icons.DELETE_OUTLINE))])],
        expand=True
    )
    
    config_min_stock = ft.TextField(label="Limite mínimo de stock", value="10", width=150, border_color=SECONDARY_COLOR)

    # --- Items General (Derecha) ---
    search_items = ft.TextField(hint_text="Buscar Item...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    
    def open_adv_config(e):
        # Ventana de configuración avanzada (Imagen 12)
        dialog = ft.AlertDialog(
            title=ft.Text("Información y config de alerta", weight=ft.FontWeight.BOLD),
            content=ft.Row([
                # Panel Izquierdo: Datos Básicos
                ft.Column([
                    ft.TextField(label="Nombre del Item", value="Coca Cola 2L"),
                    ft.TextField(label="Precio de compra", value="3000"),
                    ft.TextField(label="Precio de venta", value="4500"),
                    ft.TextField(label="Stock", value="50"),
                    ft.Text("Alerta", weight=ft.FontWeight.BOLD),
                    ft.TextField(label="Límite mínimo de stock", value="10"),
                    ft.ElevatedButton("Editar", bgcolor=PRIMARY_COLOR, color="white", width=200)
                ], tight=True, width=250),
                # Panel Derecho: Restricciones de movimiento (Imagen 12)
                ft.Container(
                    bgcolor=BACKGROUND_COLOR, padding=15, border_radius=10,
                    content=ft.Column([
                        ft.Text("Restricciones de movimiento", weight=ft.FontWeight.BOLD),
                        ft.TextField(label="Entradas restantes", value="10", read_only=True),
                        ft.TextField(label="Salidas restantes", value="10", read_only=True),
                        ft.TextField(label="Ajustes restantes", value="10", read_only=True),
                    ], tight=True, width=250)
                )
            ], spacing=20),
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    table_items = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Item")), ft.DataColumn(label=ft.Text("Compra")), ft.DataColumn(label=ft.Text("Ajuste")),
            ft.DataColumn(label=ft.Text("Ventas")), ft.DataColumn(label=ft.Text("Pérdida")), ft.DataColumn(label=ft.Text("Devolución")), ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Coca Cola 2L")), ft.DataCell(ft.Text("100")), ft.DataCell(ft.Text("0")),
                ft.DataCell(ft.Text("50")), ft.DataCell(ft.Text("0")), ft.DataCell(ft.Text("0")),
                ft.DataCell(ft.Row([ft.IconButton(ft.Icons.DELETE_OUTLINE), ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=open_adv_config)]))
            ])
        ]
    )

    # --- Layout ---
    left_panel = ft.Column([
        ft.Row([search_alerts]),
        ft.Container(table_alerts, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True),
        ft.Row([ft.Text("Limite mínimo de stock", size=12), config_min_stock], alignment=ft.MainAxisAlignment.CENTER)
    ], expand=4)

    right_panel = ft.Column([
        ft.Row([search_items, ft.ElevatedButton("Crear Inventario", icon=ft.Icons.ADD, bgcolor=PRIMARY_COLOR, color="white")]),
        ft.Container(table_items, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
    ], expand=6)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
            ft.Text("Inventario", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([left_panel, ft.VerticalDivider(width=1, color=DIVIDER_COLOR), right_panel], expand=True, spacing=20)
        ])
    )
