import flet as ft
from core.colors import *
from controllers.productos_controller import ProductosController

class ProductosView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = ProductosController(self)
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Controles de Creación ---
        self.tf_name = ft.TextField(label="Nombre", expand=True)
        self.tf_code = ft.TextField(label="Código de producto", expand=True)
        self.tf_desc = ft.TextField(label="Descripción", expand=True)
        self.tf_price_buy = ft.TextField(label="Precio de compra", expand=True)
        self.tf_price_sell = ft.TextField(label="Precio de venta", expand=True)
        self.tf_stock_actual = ft.TextField(label="Stock", expand=True)
        self.tf_stock_min = ft.TextField(label="Stock mínimo", expand=True)
        self.dd_category = ft.Dropdown(
            label="Categoría",
            options=[ft.dropdown.Option("General"), ft.dropdown.Option("Alimentos"), ft.dropdown.Option("Electrónica")],
            expand=True
        )
        self.sw_status = ft.Switch(label="Estado", value=True, active_color=PRIMARY_COLOR)
        
        # --- UI Components ---
        self.product_grid = ft.GridView(
            expand=True,
            max_extent=200,
            child_aspect_ratio=1.1, 
            spacing=15,
            run_spacing=15,
        )

        self.search_bar = ft.TextField(
            hint_text="Buscar Producto...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            on_change=lambda _: self.load_data()
        )

        create_form = ft.Container(
            expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
            content=ft.Column([
                ft.Text("Crear producto", weight=ft.FontWeight.BOLD, size=18),
                self.tf_name,
                self.tf_code,
                self.tf_desc,
                self.tf_price_buy,
                self.tf_price_sell,
                self.tf_stock_actual,
                self.tf_stock_min,
                self.dd_category,
                self.sw_status,
                ft.Text("El id del producto se genera automáticamente", size=11, color=TEXT_SECONDARY, italic=True),
                ft.Row([
                    ft.OutlinedButton("Restablecer", expand=True, on_click=self.reset_fields),
                    ft.Button("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=self.register_product)
                ], spacing=10)
            ], scroll=ft.ScrollMode.AUTO)
        )

        data_panel = ft.Container(
            expand=6,
            content=ft.Column([
                ft.Text("Productos", weight=ft.FontWeight.BOLD, size=24),
                self.search_bar,
                ft.Container(
                    content=self.product_grid,
                    bgcolor=SURFACE_COLOR, 
                    border_radius=BORDER_RADIUS, 
                    padding=15, 
                    expand=True
                )
            ])
        )

        self.content = ft.Row([create_form, data_panel], spacing=20)

    def load_data(self):
        products = self.controller.get_products(self.search_bar.value)
        self.product_grid.controls.clear()
        
        for p in products:
            card = ft.Container(
                content=ft.Column([
                    ft.Text(p.name, weight=ft.FontWeight.BOLD, size=16, no_wrap=True),
                    ft.Text(f"Código: {p.codigo_producto if p.codigo_producto else 'N/A'}", size=11, color=TEXT_SECONDARY),
                    ft.Text(p.category if p.category else "Sin categoría", size=12, color=TEXT_SECONDARY),
                    ft.Text(f"${p.price_sell:.2f}", color=PRIMARY_COLOR, weight=ft.FontWeight.W_600),
                    ft.Text(f"Stock: {p.stock}", size=11, color=TEXT_SECONDARY if p.stock > p.stock_min else DANGER_COLOR)
                ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
                padding=15,
                border_radius=10,
                border=ft.Border.all(1, DIVIDER_COLOR),
                bgcolor=SURFACE_COLOR,
                on_click=lambda _, prod=p: self.open_info_modal(prod),
                ink=True
            )
            self.product_grid.controls.append(card)
            
        self.page_ref.update()

    def show_toast(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.overlay.append(snack)
        snack.open = True
        self.page_ref.update()

    def reset_fields(self, e=None):
        self.tf_name.value = ""
        self.tf_code.value = ""
        self.tf_desc.value = ""
        self.tf_price_buy.value = ""
        self.tf_price_sell.value = ""
        self.tf_stock_actual.value = ""
        self.tf_stock_min.value = ""
        self.dd_category.value = None
        self.sw_status.value = True
        self.page_ref.update()

    def register_product(self, e):
        success, message = self.controller.register_product(
            self.tf_name.value, self.tf_desc.value, self.tf_price_buy.value,
            self.tf_price_sell.value, self.tf_stock_actual.value, self.tf_stock_min.value,
            self.dd_category.value, self.tf_code.value, self.sw_status.value
        )
        self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
        if success:
            self.reset_fields()
            self.load_data()

    def delete_prod(self, prod_id, dialog):
        success, message = self.controller.delete_product(prod_id)
        self.page_ref.pop_dialog()
        self.show_toast(message, WARNING_COLOR if success else DANGER_COLOR)
        if success:
            self.load_data()

    def open_info_modal(self, prod):
        m_name = ft.TextField(label="Nombre", value=prod.name)
        m_code = ft.TextField(label="Código de producto", value=prod.codigo_producto if prod.codigo_producto else "")
        m_desc = ft.TextField(label="Descripción", value=prod.description if prod.description else "")
        m_price_buy = ft.TextField(label="Precio de compra", value=str(prod.price_buy))
        m_price_sell = ft.TextField(label="Precio de venta", value=str(prod.price_sell))
        m_stock = ft.TextField(label="Stock", value=str(prod.stock))
        m_stock_min = ft.TextField(label="Stock mínimo", value=str(prod.stock_min))
        m_cat = ft.Dropdown(
            label="Categoría",
            value=prod.category,
            options=[ft.dropdown.Option("General"), ft.dropdown.Option("Alimentos"), ft.dropdown.Option("Electrónica")]
        )
        m_status = ft.Switch(label="Estado", value=bool(prod.status), active_color=PRIMARY_COLOR)

        def save_edit(e):
            success, message = self.controller.update_product(
                prod.id, m_name.value, m_desc.value, m_price_buy.value,
                m_price_sell.value, m_stock.value, m_stock_min.value, m_cat.value,
                m_code.value, m_status.value
            )
            if success:
                self.page_ref.pop_dialog()
                self.show_toast(message, SUCCESS_COLOR)
                self.load_data()
            else:
                self.show_toast(message, DANGER_COLOR)

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text("Info producto", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.close_dialog(dialog))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                m_name, m_code, m_desc, m_price_buy, m_price_sell, m_stock, m_stock_min, m_cat,
                m_status
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=350),
            actions=[
                ft.TextButton("Eliminar", icon=ft.Icons.DELETE, style=ft.ButtonStyle(color=DANGER_COLOR), on_click=lambda _: self.delete_prod(prod.id, dialog)),
                ft.Button("Actualizar", bgcolor=PRIMARY_COLOR, color="white", on_click=save_edit)
            ],
            bgcolor=SURFACE_COLOR
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def close_dialog(self, dialog):
        self.page_ref.pop_dialog()
        self.page_ref.update()
