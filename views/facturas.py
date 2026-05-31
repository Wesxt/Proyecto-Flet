import flet as ft
from core.colors import *
from controllers.facturas_controller import FacturasController

class FacturasView(ft.Container):
    def __init__(self, page: ft.Page, state):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.state = state
        self.controller = FacturasController(self)
        self.sales = []
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Controles de Búsqueda ---
        self.search_bar = ft.TextField(
            hint_text="Buscar por Factura ID, Cliente o Cajero...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            expand=True,
            on_change=lambda _: self.filter_sales()
        )

        self.dd_payment_filter = ft.Dropdown(
            label="Método de Pago",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Tarjeta"),
                ft.dropdown.Option("Transferencia"),
                ft.dropdown.Option("Pago Mixto")
            ],
            value="Todos",
            width=200
        )
        self.dd_payment_filter.on_change = lambda _: self.filter_sales()

        self.dd_status_filter = ft.Dropdown(
            label="Estado",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Activas"),
                ft.dropdown.Option("Anuladas")
            ],
            value="Todos",
            width=150
        )
        self.dd_status_filter.on_change = lambda _: self.filter_sales()

        filter_row = ft.Row([
            self.search_bar,
            self.dd_payment_filter,
            self.dd_status_filter
        ], spacing=15)

        # --- Tabla de Facturas ---
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Factura ID")),
                ft.DataColumn(label=ft.Text("Fecha")),
                ft.DataColumn(label=ft.Text("Cliente")),
                ft.DataColumn(label=ft.Text("Cajero")),
                ft.DataColumn(label=ft.Text("Método")),
                ft.DataColumn(label=ft.Text("Total")),
                ft.DataColumn(label=ft.Text("Estado")),
                ft.DataColumn(label=ft.Text("Acciones")),
            ],
            rows=[],
            expand=True,
            show_bottom_border=True
        )

        table_container = ft.Container(
            content=ft.Column([self.table], scroll=ft.ScrollMode.AUTO),
            bgcolor=SURFACE_COLOR,
            border_radius=BORDER_RADIUS,
            padding=15,
            expand=True,
            alignment=ft.Alignment.TOP_CENTER
        )

        self.content = ft.Column([
            ft.Text("Historial de Facturas / Ventas", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("Consulta de transacciones y anulación de facturas.", color=TEXT_SECONDARY),
            ft.Container(height=10),
            filter_row,
            ft.Container(height=10),
            table_container
        ], expand=True)

    def load_data(self):
        self.sales = self.controller.get_sales()
        self.filter_sales()

    def filter_sales(self):
        term = self.search_bar.value.lower() if self.search_bar.value else ""
        payment_filter = self.dd_payment_filter.value
        status_filter = self.dd_status_filter.value

        self.table.rows.clear()

        for s in self.sales:
            # Filtro por término de búsqueda (ID, cliente o cajero)
            client_name = s["cliente"] if s["cliente"] else "Consumidor Final"
            cashier_name = s["cajero"] if s["cajero"] else "Sistema"
            sale_id = str(s["id"])
            
            if term:
                if (term not in sale_id.lower() and 
                    term not in client_name.lower() and 
                    term not in cashier_name.lower()):
                    continue

            # Filtro por Método de Pago
            pm = s["payment_method"]
            if payment_filter != "Todos":
                if payment_filter == "Pago Mixto":
                    if not pm.startswith("Pago Mixto"):
                        continue
                elif payment_filter != pm:
                    continue

            # Filtro por Estado
            status = s["status"]
            if status_filter == "Activas" and status != 1:
                continue
            if status_filter == "Anuladas" and status != 0:
                continue

            # Renderizado de fila
            status_text = "Activa" if status == 1 else "Anulada"
            status_color = SUCCESS_COLOR if status == 1 else DANGER_COLOR
            
            # Botones de acción
            actions = [
                ft.IconButton(
                    ft.Icons.VISIBILITY_OUTLINED, 
                    icon_color=PRIMARY_COLOR, 
                    tooltip="Ver Detalle",
                    on_click=lambda _, sale_id=s["id"]: self.view_details(sale_id)
                )
            ]

            # Botón de anular (solo Admin o Supervisor y si está activa)
            can_void = self.state.role in ["Administrador", "Supervisor"]
            if status == 1:
                actions.append(
                    ft.IconButton(
                        ft.Icons.DELETE_FOREVER_OUTLINED,
                        icon_color=DANGER_COLOR if can_void else TEXT_SECONDARY,
                        disabled=not can_void,
                        tooltip="Anular Factura" if can_void else "Solo Admin/Supervisor",
                        on_click=lambda _, sale_id=s["id"]: self.confirm_void_invoice(sale_id)
                    )
                )

            self.table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"#{sale_id}", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(s["date"][:19])),
                    ft.DataCell(ft.Text(client_name)),
                    ft.DataCell(ft.Text(cashier_name)),
                    ft.DataCell(ft.Text(pm if not pm.startswith("Pago Mixto") else "Pago Mixto")),
                    ft.DataCell(ft.Text(f"${s['total']:,.2f}", weight=ft.FontWeight.W_600)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(status_text, color="white", size=11, weight=ft.FontWeight.BOLD),
                        bgcolor=status_color,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                        border_radius=5
                    )),
                    ft.DataCell(ft.Row(actions, spacing=5))
                ])
            )
            
        self.page_ref.update()

    def view_details(self, sale_id):
        details = self.controller.get_details(sale_id)
        
        details_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Código")),
                ft.DataColumn(label=ft.Text("Producto")),
                ft.DataColumn(label=ft.Text("Cant.")),
                ft.DataColumn(label=ft.Text("Precio")),
                ft.DataColumn(label=ft.Text("Subtotal")),
            ],
            rows=[]
        )

        subtotal_sum = 0
        for d in details:
            code = d["codigo_producto"] if d["codigo_producto"] else "N/A"
            qty = d["quantity"]
            price = d["price"]
            sub = qty * price
            subtotal_sum += sub
            
            details_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(code)),
                    ft.DataCell(ft.Text(d["product_name"])),
                    ft.DataCell(ft.Text(str(qty))),
                    ft.DataCell(ft.Text(f"${price:,.2f}")),
                    ft.DataCell(ft.Text(f"${sub:,.2f}")),
                ])
            )

        iva = subtotal_sum * 0.19
        total = subtotal_sum + iva

        totals_info = ft.Container(
            padding=10,
            bgcolor=BACKGROUND_COLOR,
            border_radius=8,
            content=ft.Column([
                ft.Row([ft.Text("Subtotal:", size=13), ft.Text(f"${subtotal_sum:,.2f}", weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("IVA (19%):", size=13), ft.Text(f"${iva:,.2f}", weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=DIVIDER_COLOR),
                ft.Row([ft.Text("Total Factura:", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR), ft.Text(f"${total:,.2f}", weight=ft.FontWeight.BOLD, size=15, color=PRIMARY_COLOR)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], tight=True)
        )

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text(f"Detalle de Factura #{sale_id}", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.close_dialog(dialog))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                ft.Container(
                    content=ft.Column([details_table], scroll=ft.ScrollMode.AUTO),
                    height=250
                ),
                ft.Container(height=10),
                totals_info
            ], tight=True, width=500),
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def confirm_void_invoice(self, sale_id):
        def void_invoice(e):
            success, message = self.controller.void_invoice(sale_id, self.state.username)
            self.page_ref.pop_dialog()
            if success:
                self.show_toast(message, SUCCESS_COLOR)
                self.load_data()
            else:
                self.show_toast(message, DANGER_COLOR)

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Anulación", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"¿Está seguro de que desea anular la factura #{sale_id}?\n\nEsta acción sumará de vuelta las cantidades de los productos al stock del inventario y marcará la factura como ANULADA."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog)),
                ft.ElevatedButton("Anular Factura", bgcolor=DANGER_COLOR, color="white", on_click=void_invoice)
            ],
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def show_toast(self, text, color):
        sb = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.overlay.append(sb)
        sb.open = True
        self.page_ref.update()

    def close_dialog(self, dialog):
        self.page_ref.pop_dialog()
        self.page_ref.update()
