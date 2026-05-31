import flet as ft
from core.colors import *
from controllers.pos_controller import POSController

class POSView(ft.Container):
    def __init__(self, page: ft.Page, navigate_to_billing, state):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.navigate_to_billing = navigate_to_billing
        self.state = state
        self.controller = POSController(self)
        
        self.active_register = None
        self.all_products = []
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Componentes UI ---
        self.search_products = ft.TextField(
            hint_text="Buscar producto",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            height=45,
            on_change=lambda _: self.filter_products()
        )
        
        self.search_cart = ft.TextField(
            hint_text="Buscar producto en carrito",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            height=45,
            on_change=lambda _: self.render_cart()
        )

        # Textos de Totales
        self.txt_subtotal = ft.Text("Subtotal: $ 0.00", color=TEXT_PRIMARY, size=16)
        self.txt_descuento = ft.Text("Descuento: -$ 0.00", color=TEXT_PRIMARY, size=16)
        self.txt_iva = ft.Text("IVA: $ 0.00 (19%)", color=TEXT_PRIMARY, size=16)
        self.txt_total = ft.Text("Total: $ 0.00", size=24, weight=ft.FontWeight.BOLD, color=DANGER_COLOR)

        self.cart_grid = ft.Row(wrap=True, spacing=10, run_spacing=10, expand=True, alignment=ft.MainAxisAlignment.START)
        self.products_grid_container = ft.Row(wrap=True, spacing=15, run_spacing=15, alignment=ft.MainAxisAlignment.START)

        # Panel Izquierdo (Productos)
        products_panel = ft.Container(
            expand=5,
            content=ft.Column([
                ft.Row([self.search_products]),
                ft.Container(
                    content=ft.Column([self.products_grid_container], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.Border.all(1, DIVIDER_COLOR),
                    border_radius=10,
                    padding=15
                )
            ])
        )

        # Panel Derecho (Carrito y Totales)
        cart_panel = ft.Container(
            expand=5,
            content=ft.Column([
                ft.Row([self.search_cart]),
                ft.Container(
                    content=ft.Column([self.cart_grid], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    border=ft.Border.all(1, DIVIDER_COLOR),
                    border_radius=10,
                    padding=15
                ),
                # Sección de Totales
                ft.Container(
                    bgcolor=SURFACE_COLOR,
                    padding=15,
                    border_radius=10,
                    border=ft.Border.all(1, DIVIDER_COLOR),
                    content=ft.Column([
                        ft.Row([
                            ft.Column([self.txt_subtotal, self.txt_descuento, self.txt_iva], spacing=5),
                            ft.Container(self.txt_total, alignment=ft.Alignment.BOTTOM_RIGHT, expand=True)
                        ]),
                        ft.Divider(color=DIVIDER_COLOR),
                        ft.Row([
                            ft.OutlinedButton("Cancelar", expand=True, on_click=self.cancel_cart),
                            ft.Button("Confirmar", bgcolor=TEXT_PRIMARY, color=BACKGROUND_COLOR, expand=True, on_click=lambda _: self.navigate_to_billing())
                        ], spacing=10),
                        ft.Divider(color=DIVIDER_COLOR),
                        ft.Button("Cerrar Caja", icon=ft.Icons.LOCK_OUTLINE, bgcolor=DANGER_COLOR, color="white", expand=True, on_click=lambda _: self.open_close_register_modal())
                    ])
                )
            ])
        )

        # Modals aperture controls
        self.tf_initial_amount = ft.TextField(label="Monto Inicial en Caja ($)", keyboard_type=ft.KeyboardType.NUMBER, border_color=PRIMARY_COLOR)
        
        self.modal_apertura = ft.AlertDialog(
            title=ft.Text("Apertura de Caja", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Debe abrir la caja antes de registrar ventas.", color=TEXT_SECONDARY),
                self.tf_initial_amount
            ], tight=True),
            actions=[
                ft.Button("Abrir Caja", bgcolor=PRIMARY_COLOR, color="white", on_click=self.open_cash_register)
            ],
            modal=True,
            bgcolor=SURFACE_COLOR
        )

        self.tf_actual_amount = ft.TextField(label="Monto Real contado en Caja ($)", keyboard_type=ft.KeyboardType.NUMBER, border_color=PRIMARY_COLOR)
        self.lbl_expected = ft.Text("Monto Esperado: $ 0.00", size=16, weight=ft.FontWeight.BOLD)

        self.content = ft.Column([
            ft.Text("Punto de venta", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Row([products_panel, cart_panel], spacing=30, expand=True)
        ])

    def load_data(self):
        self.all_products = self.controller.get_active_products()
        self.filter_products()
        self.render_cart()
        self.update_totals()

        # Check register
        self.active_register = self.controller.check_active_register(self.state.username)
        if not self.active_register:
            self.page_ref.show_dialog(self.modal_apertura)

    def filter_products(self):
        term = self.search_products.value.lower() if self.search_products.value else ""
        self.products_grid_container.controls.clear()
        
        for p in self.all_products:
            if term in p.name.lower():
                self.products_grid_container.controls.append(self.product_card(p.id, p.name, p.price_sell))
        self.page_ref.update()

    def update_totals(self):
        subtotal = sum(item['price'] for item in self.state.cart_items)
        iva = subtotal * 0.19
        total = subtotal + iva
        self.txt_subtotal.value = f"Subtotal: $ {subtotal:,.2f}"
        self.txt_iva.value = f"IVA: $ {iva:,.2f} (19%)"
        self.txt_total.value = f"Total: $ {total:,.2f}"
        self.page_ref.update()

    def render_cart(self):
        term = self.search_cart.value.lower() if self.search_cart.value else ""
        self.cart_grid.controls.clear()
        
        for item in self.state.cart_items:
            if term in item['name'].lower():
                self.cart_grid.controls.append(self.create_cart_card(item))
        self.page_ref.update()

    def remove_item(self, item_data):
        self.controller.remove_item_from_cart(self.state, item_data)
        self.update_totals()
        self.render_cart()

    def cancel_cart(self, e):
        self.controller.clear_cart(self.state)
        self.render_cart()
        self.update_totals()

    def add_item(self, prod_id, name, price):
        self.controller.add_item_to_cart(self.state, prod_id, name, price)
        self.update_totals()
        self.render_cart()

    def create_cart_card(self, item_data):
        card = ft.Container(
            content=ft.Stack([
                ft.Column([
                    ft.Text(item_data['name'], weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, size=14, text_align=ft.TextAlign.CENTER, no_wrap=True),
                    ft.Text(f"Precio: {item_data['price']:,.0f}", color=DANGER_COLOR, size=12)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    ft.Icon(ft.Icons.CLOSE, size=16, color=DANGER_COLOR),
                    alignment=ft.Alignment.TOP_RIGHT,
                    padding=5
                )
            ]),
            width=110, height=110, bgcolor=SURFACE_COLOR, border_radius=15,
            border=ft.Border.all(2, DANGER_COLOR),
            padding=5,
            ink=True
        )
        card.on_click = lambda _: self.remove_item(item_data)
        return card

    def product_card(self, prod_id, name, price):
        return ft.Container(
            content=ft.Column([
                ft.Text(name, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, size=14, text_align=ft.TextAlign.CENTER, no_wrap=True),
                ft.Text(f"Precio: {price:,.0f}", color=DANGER_COLOR, size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=110, height=110, bgcolor=SURFACE_COLOR, border_radius=15,
            border=ft.Border.all(1, DIVIDER_COLOR),
            padding=10, on_click=lambda _: self.add_item(prod_id, name, price), ink=True
        )

    def open_cash_register(self, e):
        try:
            amount = float(self.tf_initial_amount.value)
        except ValueError:
            return
            
        success = self.controller.open_cash_register(self.state.username, amount)
        if success:
            self.page_ref.pop_dialog()
            self.active_register = self.controller.check_active_register(self.state.username)
            self.page_ref.update()

    def open_close_register_modal(self):
        if not self.active_register:
            return
            
        # Get details from controller
        stats = self.controller.get_register_close_data(self.active_register)
        efectivo = stats["efectivo"]
        tarjeta = stats["tarjeta"]
        transferencia = stats["transferencia"]
        esperado = stats["esperado"]
        
        self.lbl_expected.value = f"Monto Esperado (Inicial + Efectivo): $ {esperado:,.2f}"
        
        def confirm_close(e, d):
            try:
                actual = float(self.tf_actual_amount.value)
            except ValueError:
                return
            
            diferencia = actual - esperado
            success = self.controller.close_cash_register(
                self.active_register.id, esperado, actual, efectivo, tarjeta, transferencia, diferencia
            )
            
            if success:
                self.page_ref.pop_dialog()
                self.page_ref.snack_bar = ft.SnackBar(ft.Text(f"Caja cerrada. Diferencia: $ {diferencia:,.2f}"), bgcolor=WARNING_COLOR if diferencia != 0 else SUCCESS_COLOR)
                self.page_ref.snack_bar.open = True
                
                # Reset initial amount text
                self.tf_initial_amount.value = ""
                # Show apertura again
                self.page_ref.show_dialog(self.modal_apertura)
                self.page_ref.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Cierre de Caja", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Ventas en Efectivo: $ {efectivo:,.2f}"),
                ft.Text(f"Ventas con Tarjeta: $ {tarjeta:,.2f}"),
                ft.Text(f"Ventas por Transferencia: $ {transferencia:,.2f}"),
                self.lbl_expected,
                ft.Divider(color=DIVIDER_COLOR),
                self.tf_actual_amount
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page_ref.pop_dialog() or self.page_ref.update()),
                ft.Button("Confirmar Cierre", bgcolor=DANGER_COLOR, color="white", on_click=lambda e: confirm_close(e, dialog))
            ],
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()
