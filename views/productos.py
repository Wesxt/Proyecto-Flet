import flet as ft
from core.colors import *
from core.database import get_connection

def ProductosView(page: ft.Page):
    """
    Catálogo y Detalle de Productos.
    """
    
    # --- Formulario de Creación ---
    tf_name = ft.TextField(label="Nombre")
    tf_desc = ft.TextField(label="Descripción", multiline=True, min_lines=2)
    tf_price_buy = ft.TextField(label="Precio de compra", expand=True)
    tf_price_sell = ft.TextField(label="Precio de venta", expand=True)
    tf_stock_actual = ft.TextField(label="Stock actual", expand=True)
    tf_stock_min = ft.TextField(label="Stock mínimo", expand=True)
    dd_category = ft.Dropdown(
        label="Categoría", 
        options=[
            ft.dropdown.Option("Alimentos"), 
            ft.dropdown.Option("Bebidas"),
            ft.dropdown.Option("Limpieza"),
            ft.dropdown.Option("Otros")
        ], 
        expand=True
    )
    
    sw_status = ft.Switch(label="Estado (On/Off)", value=True, active_color=SUCCESS_COLOR)

    # --- Lista de Productos ---
    search_bar = ft.TextField(
        hint_text="Buscar Producto...", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        on_change=lambda e: load_products(e.control.value)
    )
    
    product_grid = ft.Row(wrap=True, spacing=15, run_spacing=15)

    def load_products(search_query=""):
        conn = get_connection()
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", (f"%{search_query}%", f"%{search_query}%"))
        else:
            cursor.execute("SELECT * FROM products")
        
        products = cursor.fetchall()
        conn.close()

        product_grid.controls.clear()
        for prod in products:
            product_grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.IMAGE, size=40, color=TEXT_SECONDARY),
                        ft.Text(prod["name"], weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"S/. {prod['price_sell']:.2f}", size=12, color=SUCCESS_COLOR),
                        ft.Text(f"Stock: {prod['stock']}", size=10, color=TEXT_SECONDARY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=130, height=160, bgcolor=SURFACE_COLOR, border_radius=10,
                    padding=10, on_click=lambda e, p=prod: open_product_detail(p), ink=True
                )
            )
        page.update()

    def open_product_detail(prod):
        # Campos del editor
        edit_name = ft.TextField(label="Nombre", value=prod["name"])
        edit_desc = ft.TextField(label="Descripción", value=prod["description"], multiline=True)
        edit_price_buy = ft.TextField(label="Precio de compra", value=str(prod["price_buy"]))
        edit_price_sell = ft.TextField(label="Precio de venta", value=str(prod["price_sell"]))
        edit_stock = ft.TextField(label="Stock", value=str(prod["stock"]))
        edit_stock_min = ft.TextField(label="Stock mínimo", value=str(prod["stock_min"]))
        edit_category = ft.Dropdown(
            label="Categoría", 
            value=prod["category"],
            options=[
                ft.dropdown.Option("Alimentos"), 
                ft.dropdown.Option("Bebidas"),
                ft.dropdown.Option("Limpieza"),
                ft.dropdown.Option("Otros")
            ]
        )
        edit_status = ft.Switch(value=True if prod["status"] == 1 else False, active_color=SUCCESS_COLOR)

        def save_edit(e):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET name = ?, description = ?, price_buy = ?, price_sell = ?, stock = ?, stock_min = ?, category = ?, status = ?
                WHERE id = ?
            ''', (edit_name.value, edit_desc.value, float(edit_price_buy.value), float(edit_price_sell.value), 
                  float(edit_stock.value), float(edit_stock_min.value), edit_category.value, 
                  1 if edit_status.value else 0, prod["id"]))
            conn.commit()
            conn.close()
            dialog.open = False
            load_products(search_bar.value)
            page.update()

        def delete_prod(e):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (prod["id"],))
            conn.commit()
            conn.close()
            dialog.open = False
            load_products(search_bar.value)
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Info producto", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                edit_name, edit_desc,
                ft.Row([edit_price_buy, edit_price_sell]),
                ft.Row([edit_stock, edit_stock_min]),
                edit_category,
                ft.Row([ft.Text("Estado"), edit_status]),
            ], tight=True, scroll=ft.ScrollMode.AUTO, spacing=15),
            actions=[
                ft.TextButton("Eliminar", icon=ft.Icons.DELETE, style=ft.ButtonStyle(color=DANGER_COLOR), on_click=delete_prod),
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                ft.ElevatedButton("Guardar", bgcolor=PRIMARY_COLOR, color="white", on_click=save_edit)
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def register_product(e):
        if not all([tf_name.value, tf_price_sell.value, tf_stock_actual.value]):
            page.snack_bar = ft.SnackBar(ft.Text("Nombre, precio venta y stock son obligatorios"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price_buy, price_sell, stock, stock_min, category, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tf_name.value, tf_desc.value, float(tf_price_buy.value or 0), float(tf_price_sell.value), 
                  float(tf_stock_actual.value or 0), float(tf_stock_min.value or 0), dd_category.value, 
                  1 if sw_status.value else 0))
            conn.commit()
            conn.close()
            
            reset_fields(None)
            page.snack_bar = ft.SnackBar(ft.Text("Producto registrado con éxito"), bgcolor=SUCCESS_COLOR)
            page.snack_bar.open = True
            load_products(search_bar.value)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()

    def reset_fields(e):
        tf_name.value = ""
        tf_desc.value = ""
        tf_price_buy.value = ""
        tf_price_sell.value = ""
        tf_stock_actual.value = ""
        tf_stock_min.value = ""
        dd_category.value = None
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

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
                ft.OutlinedButton("Restablecer", expand=True, on_click=reset_fields),
                ft.ElevatedButton("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=register_product)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    list_panel = ft.Column([
        ft.Text("Productos", weight=ft.FontWeight.BOLD, size=20),
        search_bar,
        ft.Container(ft.Column([product_grid], scroll=ft.ScrollMode.AUTO), expand=True, padding=10)
    ], expand=6)

    # Cargar inicialmente
    load_products()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([create_form, list_panel], spacing=20)
    )
