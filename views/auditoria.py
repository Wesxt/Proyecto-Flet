import flet as ft
from core.colors import *
from controllers.auditoria_controller import AuditoriaController

class AuditoriaView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = AuditoriaController(self)
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        self.search_bar = ft.TextField(
            hint_text="Buscar evento...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            on_change=lambda _: self.load_data()
        )
        
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Tipo de evento")), 
                ft.DataColumn(label=ft.Text("Fecha de generación")), 
                ft.DataColumn(label=ft.Text("Acciones"))
            ],
            rows=[],
            expand=True
        )

        self.content = ft.Column([
            ft.Text("Auditoría", size=24, weight=ft.FontWeight.BOLD),
            self.search_bar,
            ft.Container(self.table, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
        ])

    def load_data(self):
        events = self.controller.get_audit_events(self.search_bar.value)
        self.table.rows.clear()
        
        for ev in events:
            self.table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(ev.event_type)),
                    ft.DataCell(ft.Text(ev.timestamp)),
                    ft.DataCell(
                        ft.IconButton(
                            ft.Icons.ARROW_FORWARD_ROUNDED, 
                            on_click=lambda _, event=ev: self.open_audit_detail(event)
                        )
                    )
                ])
            )
        self.page_ref.update()

    def open_audit_detail(self, ev):
        content = ft.Column(tight=True, spacing=15, scroll=ft.ScrollMode.AUTO)
        event_type = ev.event_type
        details = ev.details
        
        if event_type == "Inicio de Sesión":
            content.controls = [
                ft.TextField(label="Usuario", value=details.get("usuario"), read_only=True),
                ft.TextField(label="Fecha de inicio de sesión exacta", value=details.get("fecha_exacta"), read_only=True),
                ft.TextField(label="Rol", value=details.get("rol"), read_only=True),
            ]
        elif event_type == "Venta":
            content.controls = [
                ft.TextField(label="Producto vendido", value=details.get("producto"), read_only=True),
                ft.TextField(label="Unidades vendidas", value=details.get("unidades"), read_only=True),
                ft.TextField(label="Venta realizada con el usuario", value=details.get("usuario"), read_only=True),
                ft.TextField(label="Rol del usuario", value=details.get("rol"), read_only=True),
                ft.TextField(label="Nombre del cliente", value=details.get("cliente"), read_only=True),
                ft.TextField(label="Metodo de pago", value=details.get("metodo_pago"), read_only=True),
            ]
        elif event_type == "Anulación":
            content.controls = [
                ft.TextField(label="Código de factura", value=details.get("factura"), read_only=True),
                ft.TextField(label="Fecha de anulación", value=details.get("fecha_exacta"), read_only=True),
                ft.TextField(label="Nombre del cliente", value=details.get("cliente"), read_only=True),
                ft.TextField(label="Total anulado", value=details.get("total"), color=DANGER_COLOR, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD), read_only=True),
            ]
        elif event_type == "Cambio de Inventario":
            content.controls = [
                ft.TextField(label="Item", value=details.get("item"), read_only=True),
                ft.RadioGroup(
                    content=ft.Row([
                        ft.Radio(value="entrada", label="Entrada"), 
                        ft.Radio(value="salida", label="Salida")
                    ]),
                    value=details.get("movimiento"),
                    disabled=True
                ),
                ft.TextField(label="Fecha de evento", value=details.get("fecha_exacta"), read_only=True),
                ft.TextField(label="Unidades", value=details.get("unidades"), read_only=True),
                ft.TextField(label="Stock restante", value=details.get("restante"), read_only=True),
            ]
        elif event_type == "Cambio de Producto":
            content.controls = [
                ft.Container(ft.Icon(ft.Icons.IMAGE, size=50), alignment=ft.Alignment.CENTER),
                ft.TextField(label="Nombre del producto", value=details.get("nombre"), read_only=True),
                ft.RadioGroup(
                    content=ft.Row([
                        ft.Radio(value="venta", label="Venta"), 
                        ft.Radio(value="compra", label="Compra")
                    ]),
                    value=details.get("tipo"),
                    disabled=True
                ),
                ft.TextField(label="Antiguo precio", value=details.get("antiguo_precio"), read_only=True),
                ft.TextField(label="Nuevo precio", value=details.get("nuevo_precio"), color=SUCCESS_COLOR, read_only=True),
            ]

        dialog = ft.AlertDialog(
            title=ft.Text(f"Evento: {event_type}", weight=ft.FontWeight.BOLD),
            content=content,
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()
