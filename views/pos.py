import flet as ft
from core.colors import *

def POSView(page: ft.Page, navigate_to_billing):
    """
    Vista Punto de Venta (Imagen 5).
    Incluye buscadores, cuadrícula de productos y panel de totales.
    """
    
    # --- Estado Local ---
    cart_items = []
    
    # --- Componentes UI ---
    search_products = ft.TextField(
        hint_text="Buscar producto...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        border_radius=10
    )
    
    search_cart = ft.TextField(
        hint_text="Buscar en carrito...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        border_radius=10
    )

    # Textos de Totales (Imagen 5)
    txt_subtotal = ft.Text("$ 0.00", color=TEXT_PRIMARY)
    txt_descuento = ft.Text("$ 0.00", color=TEXT_PRIMARY)
    txt_iva = ft.Text("$ 0.00 (19%)", color=TEXT_PRIMARY)
    txt_total = ft.Text("$ 0.00", size=24, weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR)

    cart_list = ft.ListView(expand=True, spacing=10, padding=10)

    def update_totals():
        subtotal = sum(item['price'] for item in cart_items)
        iva = subtotal * 0.19
        total = subtotal + iva
        txt_subtotal.value = f"$ {subtotal:.2f}"
        txt_iva.value = f"$ {iva:.2f} (19%)"
        txt_total.value = f"$ {total:.2f}"
        page.update()

    def add_item(name, price):
        cart_items.append({"name": name, "price": price})
        cart_list.controls.append(
            ft.ListTile(
                title=ft.Text(name, color=TEXT_PRIMARY),
                subtitle=ft.Text(f"$ {price:.2f}", color=TEXT_SECONDARY),
                trailing=ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR, on_click=lambda _: remove_item(name))
            )
        )
        update_totals()

    def remove_item(name):
        # Lógica simplificada de eliminación
        for i, item in enumerate(cart_items):
            if item['name'] == name:
                cart_items.pop(i)
                cart_list.controls.pop(i)
                break
        update_totals()

    # Generador de tarjetas de producto
    def product_card(name, price):
        return ft.Container(
            content=ft.Column([
                ft.Container(ft.Icon(ft.Icons.IMAGE, size=40, color=TEXT_SECONDARY), alignment=ft.Alignment.CENTER, height=80),
                ft.Text(name, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(f"$ {price:.2f}", color=SUCCESS_COLOR)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=130, height=160, bgcolor=SURFACE_COLOR, border_radius=BORDER_RADIUS,
            padding=10, on_click=lambda _: add_item(name, price), ink=True
        )

    # --- Layout ---
    # Cuadrícula de productos (Izquierda)
    products_grid = ft.Column([
        ft.Row([search_products]),
        ft.Divider(color=DIVIDER_COLOR),
        ft.Row(
            wrap=True, spacing=15, run_spacing=15,
            controls=[
                product_card("Hamburguesa", 15000),
                product_card("Papas Fritas", 8000),
                product_card("Refresco", 4500),
                product_card("Pizza", 12000),
                product_card("Helado", 3500),
                product_card("Agua", 2000),
            ]
        )
    ], expand=7, scroll=ft.ScrollMode.AUTO)

    # Panel de Carrito y Totales (Derecha)
    cart_panel = ft.Container(
        expand=3, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Row([search_cart]),
            ft.Divider(color=DIVIDER_COLOR),
            cart_list,
            ft.Divider(color=DIVIDER_COLOR),
            # Sección de Totales (Imagen 5)
            ft.Column([
                ft.Row([ft.Text("Subtotal:", color=TEXT_SECONDARY), txt_subtotal], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Descuento:", color=TEXT_SECONDARY), txt_descuento], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("IVA (19%):", color=TEXT_SECONDARY), txt_iva], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Total:", weight=ft.FontWeight.BOLD, size=20), txt_total], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=5),
            ft.Row([
                ft.Button("Cancelar", bgcolor=DANGER_COLOR, color="white", expand=True, on_click=lambda _: (cart_items.clear(), cart_list.controls.clear(), update_totals())),
                ft.Button("Confirmar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=lambda _: navigate_to_billing())
            ], spacing=10)
        ])
    )

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([products_grid, ft.VerticalDivider(width=1, color=DIVIDER_COLOR), cart_panel], spacing=20)
    )
