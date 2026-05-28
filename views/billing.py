import flet as ft
from core.colors import *
from controllers.billing_controller import BillingController
import datetime

class BillingView(ft.Container):
    def __init__(self, page: ft.Page, navigate_to_pos, state):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.navigate_to_pos = navigate_to_pos
        self.state = state
        self.controller = BillingController(self)
        
        self.all_clients = []
        self.cart_items = state.cart_items
        
        # Totales del Carrito
        self.subtotal = sum(item['price'] for item in self.cart_items)
        self.iva = self.subtotal * 0.19
        self.total = self.subtotal + self.iva
        self.items_count = len(self.cart_items)

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Componentes Izquierda (Búsqueda de Clientes) ---
        btn_back = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=TEXT_PRIMARY,
            tooltip="Volver a los productos en carrito",
            on_click=lambda _: self.navigate_to_pos()
        )
        
        self.search_client = ft.TextField(
            hint_text="Buscar Cliente", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR, 
            height=45,
            on_change=lambda _: self.filter_clients()
        )
        
        self.client_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD)), 
                ft.DataColumn(label=ft.Text("Ultima compra", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            expand=True,
            heading_row_color=BACKGROUND_COLOR,
            show_bottom_border=True
        )

        info_text = ft.Text(
            "Esto sirve como plantilla para completar más rápido la facturación con datos no sensibles cuando se seleccione un cliente frecuente registrado y también para registrar su compra",
            color=DANGER_COLOR, size=12, italic=True
        )

        left_panel = ft.Container(
            expand=4,
            content=ft.Column([
                ft.Row([btn_back, self.search_client], expand=False),
                ft.Container(
                    content=ft.Column([self.client_table], scroll=ft.ScrollMode.AUTO),
                    bgcolor=SURFACE_COLOR, border_radius=10, border=ft.Border.all(1, DIVIDER_COLOR), expand=True
                ),
                info_text
            ])
        )

        # --- Componentes Derecha (Formulario Adaptativo) ---
        self.tf_name = ft.TextField(label="Nombre y apellido")
        self.dd_doc_type = ft.Dropdown(
            label="Tipo de documento",
            options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT")],
            value="Cédula de ciudadanía"
        )
        self.tf_doc_num = ft.TextField(label="Número de documento")
        
        # Campos de Tarjeta
        self.card_fields = ft.Column([
            ft.TextField(label="Numero de la tarjeta"),
            ft.TextField(label="Nombre del titular"),
            ft.Row([
                ft.TextField(label="Vencimiento", expand=True),
                ft.TextField(label="Código de seguridad", expand=True, password=True),
            ]),
            ft.Row([
                ft.Dropdown(options=[ft.dropdown.Option("Cédula de ciudadanía")], value="Cédula de ciudadanía", expand=True),
                ft.TextField(label="Número de documento", expand=True)
            ])
        ], visible=False)

        self.cash_info = ft.Text("Si es efectivo no hay más datos que pedir sobre el método de pago", color=SUCCESS_COLOR, size=12, italic=True, visible=True)

        self.payment_method = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="tarjeta", label="Tarjeta de credito/debito"),
                ft.Radio(value="efectivo", label="Efectivo"),
            ]),
            value="efectivo",
            on_change=self.on_payment_change
        )

        # Totales y Métricas
        now = datetime.datetime.now()
        metrics_panel = ft.Container(
            padding=10,
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Subtotal: $ {self.subtotal:.0f}", color=DANGER_COLOR, size=12),
                    ft.Text("Descuento: -$ 0", color=DANGER_COLOR, size=12),
                    ft.Text(f"IVA: $ {self.iva:.0f} (19%)", color=DANGER_COLOR, size=12),
                    ft.Text(f"Total: $ {self.total:.0f}", color=DANGER_COLOR, weight=ft.FontWeight.BOLD),
                ]),
                ft.Column([
                    ft.Text(f"Ítems: {self.items_count}", size=12),
                    ft.Text(f"Fecha: {now.strftime('%d/%m/%Y')}", size=12),
                    ft.Text(f"Hora: {now.strftime('%H:%M %p')}", size=12),
                ]),
                ft.Column([
                    ft.Text("Codigo de Fac:", size=12),
                    ft.Text("FAC-N/A", weight=ft.FontWeight.BOLD),
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        self.sw_register_client = ft.Switch(active_color=TEXT_PRIMARY)

        right_panel = ft.Container(
            expand=6,
            bgcolor=SURFACE_COLOR,
            padding=20,
            border_radius=15,
            border=ft.Border.all(1, DIVIDER_COLOR),
            content=ft.Column([
                ft.Text("Facturación", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                self.tf_name,
                ft.Row([self.dd_doc_type, self.tf_doc_num]),
                ft.Container(
                    padding=10, border=ft.Border.all(1, DIVIDER_COLOR), border_radius=10,
                    content=ft.Column([
                        ft.Text("Método de pago", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.payment_method,
                            ft.VerticalDivider(color=DIVIDER_COLOR),
                            ft.Column([self.card_fields, self.cash_info], expand=True)
                        ])
                    ])
                ),
                ft.Divider(color=DIVIDER_COLOR),
                metrics_panel,
                ft.Row([
                    ft.Text("Registrar nuevo cliente frecuente", size=14, color=TEXT_SECONDARY),
                    self.sw_register_client
                ], alignment=ft.MainAxisAlignment.START),
                ft.Row([
                    ft.OutlinedButton("Restablecer", expand=True, on_click=self.reset_fields),
                    ft.Button("Facturar", bgcolor=TEXT_PRIMARY, color=BACKGROUND_COLOR, expand=True, on_click=self.process_billing)
                ], spacing=10)
            ], scroll=ft.ScrollMode.AUTO)
        )

        self.content = ft.Row([left_panel, right_panel], spacing=30)

    def load_data(self):
        self.all_clients = self.controller.get_all_clients()
        self.filter_clients()

    def filter_clients(self):
        term = self.search_client.value.lower() if self.search_client.value else ""
        self.client_table.rows.clear()
        
        for c in self.all_clients:
            if term in c.fullname.lower() or (c.doc_num and term in c.doc_num):
                last_p = c.last_purchase[:10] if c.last_purchase else "N/A"
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c.fullname)), 
                        ft.DataCell(ft.Text(last_p))
                    ],
                    on_select_change=lambda e, client=c: self.select_client(client)
                )
                self.client_table.rows.append(row)
        self.page_ref.update()

    def select_client(self, client):
        self.tf_name.value = client.fullname
        if client.doc_type:
            self.dd_doc_type.value = client.doc_type
        if client.doc_num:
            self.tf_doc_num.value = client.doc_num
        self.sw_register_client.value = False
        self.sw_register_client.disabled = True
        self.page_ref.update()

    def on_payment_change(self, e):
        is_tarjeta = (e.control.value == "tarjeta")
        self.card_fields.visible = is_tarjeta
        self.cash_info.visible = not is_tarjeta
        self.page_ref.update()

    def reset_fields(self, e=None):
        self.tf_name.value = ""
        self.tf_doc_num.value = ""
        self.sw_register_client.value = False
        self.sw_register_client.disabled = False
        self.page_ref.update()

    def show_toast(self, text, color):
        sb = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.overlay.append(sb)
        sb.open = True
        self.page_ref.update()

    def process_billing(self, e):
        if not self.cart_items:
            self.show_toast("El carrito está vacío", DANGER_COLOR)
            return

        try:
            # Delegate transaction processing to controller
            sale_id = self.controller.process_billing(
                username=self.state.username,
                client_fullname=self.tf_name.value,
                doc_type=self.dd_doc_type.value,
                doc_num=self.tf_doc_num.value,
                payment_method_val=self.payment_method.value,
                register_client_flag=self.sw_register_client.value,
                total=self.total,
                cart_items=self.cart_items
            )
            
            if sale_id:
                self.show_toast("Factura registrada exitosamente", SUCCESS_COLOR)
                self.state.cart_items.clear()
                self.navigate_to_pos()
        except Exception as ex:
            self.show_toast(f"Error al facturar: {str(ex)}", DANGER_COLOR)
