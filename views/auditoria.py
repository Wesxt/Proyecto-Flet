import flet as ft
from core.colors import *

def AuditoriaView(page: ft.Page):
    """
    Registro de Auditoría (Imágenes 16-21).
    Log de eventos con detalles extendidos en ventanas emergentes.
    """
    
    def open_audit_detail(event_type):
        # Lógica de detalles según el tipo de evento (Imágenes 17-21)
        content = ft.Column(tight=True, spacing=15, scroll=ft.ScrollMode.AUTO)
        
        if event_type == "Inicio de Sesión":
            content.controls = [
                ft.TextField(label="Usuario", value="admin_1", read_only=True),
                ft.TextField(label="Fecha de inicio de sesión exacta", value="12/04/2026 08:00:45", read_only=True),
                ft.TextField(label="Rol", value="Administrador", read_only=True),
            ]
        elif event_type == "Venta":
            content.controls = [
                ft.TextField(label="Producto vendido", value="Coca Cola 2L", read_only=True),
                ft.TextField(label="Unidades vendidas", value="2", read_only=True),
                ft.TextField(label="Venta realizada con el usuario", value="cajero_1", read_only=True),
                ft.TextField(label="Rol del usuario", value="Cajero", read_only=True),
                ft.TextField(label="Nombre del cliente", value="Consumidor Final", read_only=True),
                ft.TextField(label="Metodo de pago", value="Efectivo", read_only=True),
            ]
        elif event_type == "Anulación":
            content.controls = [
                ft.TextField(label="Código de factura", value="FAC-000123", read_only=True),
                ft.TextField(label="Fecha de anulación", value="12/04/2026 15:30", read_only=True),
                ft.TextField(label="Nombre del cliente", value="Juan Pérez", read_only=True),
                ft.TextField(label="Total anulado", value="$ 17,850", color=DANGER_COLOR, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD), read_only=True),
            ]
        elif event_type == "Cambio de Inventario":
            content.controls = [
                ft.TextField(label="Item", value="Agua", read_only=True),
                ft.Row([ft.Radio(value="in", label="Entrada"), ft.Radio(value="out", label="Salida")]),
                ft.TextField(label="Fecha de evento", value="12/04/2026 10:00", read_only=True),
                ft.TextField(label="Unidades", value="50", read_only=True),
                ft.TextField(label="Stock restante", value="55", read_only=True),
            ]
        elif event_type == "Cambio de Producto":
            content.controls = [
                ft.Container(ft.Icon(ft.Icons.IMAGE, size=50), alignment=ft.Alignment.CENTER),
                ft.TextField(label="Nombre del producto", value="Hamburguesa", read_only=True),
                ft.Row([ft.Radio(label="Venta", value="venta"), ft.Radio(label="Compra", value="compra")]),
                ft.TextField(label="Antiguo precio", value="12000", read_only=True),
                ft.TextField(label="Nuevo precio", value="15000", color=SUCCESS_COLOR, read_only=True),
            ]

        dialog = ft.AlertDialog(
            title=ft.Text(f"Evento: {event_type}", weight=ft.FontWeight.BOLD),
            content=content,
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # --- Tabla Principal (Imagen 16) ---
    search_bar = ft.TextField(hint_text="Buscar evento...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    table = ft.DataTable(
        columns=[ft.DataColumn(label=ft.Text("Tipo de evento")), ft.DataColumn(label=ft.Text("Fecha de generación")), ft.DataColumn(label=ft.Text("Acciones"))],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Inicio de Sesión")), ft.DataCell(ft.Text("12/04/2026 08:00")), ft.DataCell(ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=lambda _: open_audit_detail("Inicio de Sesión")))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Venta")), ft.DataCell(ft.Text("12/04/2026 14:20")), ft.DataCell(ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=lambda _: open_audit_detail("Venta")))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Anulación")), ft.DataCell(ft.Text("12/04/2026 15:30")), ft.DataCell(ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=lambda _: open_audit_detail("Anulación")))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Cambio de Inventario")), ft.DataCell(ft.Text("12/04/2026 10:00")), ft.DataCell(ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=lambda _: open_audit_detail("Cambio de Inventario")))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Cambio de Producto")), ft.DataCell(ft.Text("12/04/2026 11:15")), ft.DataCell(ft.IconButton(ft.Icons.ARROW_FORWARD_ROUNDED, on_click=lambda _: open_audit_detail("Cambio de Producto")))]),
        ],
        expand=True
    )

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
            ft.Text("Auditoría", size=24, weight=ft.FontWeight.BOLD),
            search_bar,
            ft.Container(table, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
        ])
    )
