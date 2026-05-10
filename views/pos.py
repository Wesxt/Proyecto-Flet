import flet as ft
from core.colors import *
from core.database import get_connection

def POSView(page: ft.Page, navigate_to_billing, state):
    """
    Vista Punto de Venta (Imagen 5).
    Conectado a la base de datos para cargar productos reales.
    """
    
    # --- Estado Local y Global ---
    cart_items = state.cart_items
    all_products = [] # Caché de productos
    active_register_id = None
    
    # --- Verificación de Caja ---
    def check_active_register():
        nonlocal active_register_id
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (state.username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False
            
        user_id = user["id"]
        cursor.execute("SELECT id FROM cash_registers WHERE user_id = ? AND status = 1", (user_id,))
        reg = cursor.fetchone()
        conn.close()
        
        if reg:
            active_register_id = reg["id"]
            return True
        return False
    
    # --- Componentes UI ---
    search_products = ft.TextField(
        hint_text="Buscar producto",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        border_radius=10,
        height=45,
        on_change=lambda _: filter_products()
    )
    
    search_cart = ft.TextField(
        hint_text="Buscar producto en carrito",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        border_radius=10,
        height=45,
        on_change=lambda _: render_cart()
    )

    # Textos de Totales
    txt_subtotal = ft.Text("Subtotal: $ 0.00", color=TEXT_PRIMARY, size=16)
    txt_descuento = ft.Text("Descuento: -$ 0.00", color=TEXT_PRIMARY, size=16)
    txt_iva = ft.Text("IVA: $ 0.00 (19%)", color=TEXT_PRIMARY, size=16)
    txt_total = ft.Text("Total: $ 0.00", size=24, weight=ft.FontWeight.BOLD, color=DANGER_COLOR)

    cart_grid = ft.Row(wrap=True, spacing=10, run_spacing=10, expand=True, alignment=ft.MainAxisAlignment.START)
    products_grid_container = ft.Row(wrap=True, spacing=15, run_spacing=15, alignment=ft.MainAxisAlignment.START)

    def load_products_from_db():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price_sell, stock FROM products WHERE status = 1")
        nonlocal all_products
        all_products = cursor.fetchall()
        conn.close()
        filter_products()

    def filter_products():
        term = search_products.value.lower() if search_products.value else ""
        products_grid_container.controls.clear()
        
        for p in all_products:
            if term in p['name'].lower():
                products_grid_container.controls.append(product_card(p['id'], p['name'], p['price_sell']))
        page.update()

    def update_totals():
        subtotal = sum(item['price'] for item in cart_items)
        iva = subtotal * 0.19
        total = subtotal + iva
        txt_subtotal.value = f"Subtotal: $ {subtotal:,.2f}"
        txt_iva.value = f"IVA: $ {iva:,.2f} (19%)"
        txt_total.value = f"Total: $ {total:,.2f}"
        page.update()

    def render_cart():
        term = search_cart.value.lower() if search_cart.value else ""
        cart_grid.controls.clear()
        
        for item in cart_items:
            if term in item['name'].lower():
                cart_grid.controls.append(create_cart_card(item))
        page.update()

    def remove_item(item_data):
        if item_data in cart_items:
            cart_items.remove(item_data)
            update_totals()
            render_cart()

    def create_cart_card(item_data):
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
        card.on_click = lambda _: remove_item(item_data)
        return card

    def add_item(prod_id, name, price):
        item_data = {"id": prod_id, "name": name, "price": price}
        cart_items.append(item_data)
        update_totals()
        render_cart()

    # Generador de tarjetas de producto
    def product_card(prod_id, name, price):
        return ft.Container(
            content=ft.Column([
                ft.Text(name, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, size=14, text_align=ft.TextAlign.CENTER, no_wrap=True),
                ft.Text(f"Precio: {price:,.0f}", color=DANGER_COLOR, size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=110, height=110, bgcolor=SURFACE_COLOR, border_radius=15,
            border=ft.Border.all(1, DIVIDER_COLOR),
            padding=10, on_click=lambda _: add_item(prod_id, name, price), ink=True
        )

    # --- Layout ---
    # Panel Izquierdo (Productos)
    products_panel = ft.Container(
        expand=5,
        content=ft.Column([
            ft.Row([search_products]),
            ft.Container(
                content=ft.Column([products_grid_container], scroll=ft.ScrollMode.AUTO),
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
            ft.Row([search_cart]),
            ft.Container(
                content=ft.Column([cart_grid], scroll=ft.ScrollMode.AUTO),
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
                        ft.Column([txt_subtotal, txt_descuento, txt_iva], spacing=5),
                        ft.Container(txt_total, alignment=ft.Alignment.BOTTOM_RIGHT, expand=True)
                    ]),
                    ft.Divider(color=DIVIDER_COLOR),
                    ft.Row([
                        ft.OutlinedButton("Cancelar", expand=True, on_click=lambda _: (cart_items.clear(), render_cart(), update_totals())),
                        ft.Button("Confirmar", bgcolor=TEXT_PRIMARY, color=BACKGROUND_COLOR, expand=True, on_click=lambda _: navigate_to_billing())
                    ], spacing=10),
                    ft.Divider(color=DIVIDER_COLOR),
                    ft.Button("Cerrar Caja", icon=ft.Icons.LOCK_OUTLINE, bgcolor=DANGER_COLOR, color="white", expand=True, on_click=lambda _: open_close_register_modal())
                ])
            )
        ])
    )
    
    # --- Apertura y Cierre de Caja Modals ---
    tf_initial_amount = ft.TextField(label="Monto Inicial en Caja ($)", keyboard_type=ft.KeyboardType.NUMBER, border_color=PRIMARY_COLOR)
    
    def open_cash_register(e, dialog):
        try:
            amount = float(tf_initial_amount.value)
        except ValueError:
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (state.username,))
        user = cursor.fetchone()
        user_id = user["id"]
        
        cursor.execute('''
            INSERT INTO cash_registers (user_id, initial_amount, status)
            VALUES (?, ?, 1)
        ''', (user_id, amount))
        conn.commit()
        conn.close()
        
        page.pop_dialog()
        check_active_register()
        page.update()

    modal_apertura = ft.AlertDialog(
        title=ft.Text("Apertura de Caja", weight=ft.FontWeight.BOLD),
        content=ft.Column([
            ft.Text("Debe abrir la caja antes de registrar ventas.", color=TEXT_SECONDARY),
            tf_initial_amount
        ], tight=True),
        actions=[
            ft.Button("Abrir Caja", bgcolor=PRIMARY_COLOR, color="white", on_click=lambda e: open_cash_register(e, modal_apertura))
        ],
        modal=True,
        bgcolor=SURFACE_COLOR
    )

    tf_actual_amount = ft.TextField(label="Monto Real contado en Caja ($)", keyboard_type=ft.KeyboardType.NUMBER, border_color=PRIMARY_COLOR)
    lbl_expected = ft.Text("Monto Esperado: $ 0.00", size=16, weight=ft.FontWeight.BOLD)
    
    def open_close_register_modal():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cash_registers WHERE id = ?", (active_register_id,))
        reg = cursor.fetchone()
        
        # Calcular ventas desde opening_time
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN payment_method = 'Efectivo' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN payment_method = 'Tarjeta' THEN total ELSE 0 END) as total_tarjeta,
                SUM(total) as total_ventas
            FROM sales 
            WHERE user_id = ? AND date >= ?
        ''', (reg["user_id"], reg["opening_time"]))
        res = cursor.fetchone()
        conn.close()
        
        efectivo = res["total_efectivo"] or 0
        tarjeta = res["total_tarjeta"] or 0
        esperado = reg["initial_amount"] + efectivo
        
        lbl_expected.value = f"Monto Esperado (Inicial + Efectivo): $ {esperado:,.2f}"
        
        def confirm_close(e, d):
            try:
                actual = float(tf_actual_amount.value)
            except ValueError:
                return
            
            diferencia = actual - esperado
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE cash_registers 
                SET closing_time = CURRENT_TIMESTAMP, 
                    expected_amount = ?, 
                    actual_amount = ?, 
                    cash_sales = ?, 
                    card_sales = ?, 
                    difference = ?, 
                    status = 0
                WHERE id = ?
            ''', (esperado, actual, efectivo, tarjeta, diferencia, active_register_id))
            conn.commit()
            conn.close()
            
            page.pop_dialog()
            page.snack_bar = ft.SnackBar(ft.Text(f"Caja cerrada. Diferencia: $ {diferencia:,.2f}"), bgcolor=WARNING_COLOR if diferencia != 0 else SUCCESS_COLOR)
            page.snack_bar.open = True
            
            # Show apertura again
            page.show_dialog(modal_apertura)
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Cierre de Caja", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text(f"Ventas en Efectivo: $ {efectivo:,.2f}"),
                ft.Text(f"Ventas con Tarjeta: $ {tarjeta:,.2f}"),
                lbl_expected,
                ft.Divider(color=DIVIDER_COLOR),
                tf_actual_amount
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog() or page.update()),
                ft.Button("Confirmar Cierre", bgcolor=DANGER_COLOR, color="white", on_click=lambda e: confirm_close(e, dialog))
            ],
            bgcolor=SURFACE_COLOR
        )
        if dialog not in page.overlay:
            page.show_dialog(dialog)
        page.update()

    load_products_from_db()
    render_cart()
    update_totals()

    if not check_active_register():
        page.show_dialog(modal_apertura)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
            ft.Text("Punto de venta", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Row([products_panel, cart_panel], spacing=30, expand=True)
        ])
    )
