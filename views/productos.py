import flet as ft
from core.colors import *
from core.database import get_connection

def ProductosView(page: ft.Page):
    """
    Módulo de Productos simplificado (sin imágenes para mayor estabilidad).
    """
    
    # --- Controles de Creación ---
    tf_name = ft.TextField(label="Nombre", expand=True)
    tf_desc = ft.TextField(label="Descripción", expand=True)
    tf_price_buy = ft.TextField(label="Precio de compra", expand=True)
    tf_price_sell = ft.TextField(label="Precio de venta", expand=True)
    tf_stock_actual = ft.TextField(label="Stock", expand=True)
    tf_stock_min = ft.TextField(label="Stock mínimo", expand=True)
    dd_category = ft.Dropdown(
        label="Categoría",
        options=[ft.dropdown.Option("General"), ft.dropdown.Option("Alimentos"), ft.dropdown.Option("Electrónica")],
        expand=True
    )
    sw_status = ft.Switch(label="Estado", value=True, active_color=PRIMARY_COLOR)
    
    # --- UI Components ---
    product_grid = ft.GridView(
        expand=True,
        max_extent=200,
        child_aspect_ratio=1.2, # Ajustado para que quepa bien el texto sin imagen
        spacing=15,
        run_spacing=15,
    )

    search_bar = ft.TextField(
        hint_text="Buscar Producto...", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        on_change=lambda _: load_products()
    )

    def show_toast(text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def reset_fields(e=None):
        tf_name.value = ""
        tf_desc.value = ""
        tf_price_buy.value = ""
        tf_price_sell.value = ""
        tf_stock_actual.value = ""
        tf_stock_min.value = ""
        dd_category.value = None
        sw_status.value = True
        page.update()

    def load_products():
        search_term = search_bar.value.lower() if search_bar.value else ""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", (f"%{search_term}%", f"%{search_term}%"))
        products = cursor.fetchall()
        conn.close()

        product_grid.controls.clear()
        
        for p in products:
            card = ft.Container(
                content=ft.Column([
                    ft.Text(p["name"], weight=ft.FontWeight.BOLD, size=16, no_wrap=True),
                    ft.Text(p["category"] if p["category"] else "Sin categoría", size=12, color=TEXT_SECONDARY),
                    ft.Text(f"${p['price_sell']:.2f}", color=PRIMARY_COLOR, weight=ft.FontWeight.W_600),
                    ft.Text(f"Stock: {p['stock']}", size=11, color=TEXT_SECONDARY if p['stock'] > p['stock_min'] else DANGER_COLOR)
                ], spacing=5, alignment=ft.MainAxisAlignment.CENTER),
                padding=15,
                border_radius=10,
                border=ft.Border.all(1, DIVIDER_COLOR),
                bgcolor=SURFACE_COLOR,
                on_click=lambda _, prod=p: open_info_modal(prod),
                ink=True
            )
            product_grid.controls.append(card)
            
        page.update()

    def register_product(e):
        if not tf_name.value or not tf_price_sell.value:
            show_toast("El nombre y precio de venta son obligatorios", DANGER_COLOR)
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO products (name, description, price_buy, price_sell, stock, stock_min, category, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tf_name.value, tf_desc.value, float(tf_price_buy.value or 0), float(tf_price_sell.value), 
                float(tf_stock_actual.value or 0), float(tf_stock_min.value or 0), dd_category.value, 
                1 if sw_status.value else 0
            ))
            conn.commit()
            show_toast("Producto registrado con éxito", SUCCESS_COLOR)
            reset_fields()
            load_products()
        except Exception as ex:
            show_toast(f"Error: {str(ex)}", DANGER_COLOR)
        finally:
            conn.close()

    def delete_prod(prod_id, dialog):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        conn.commit()
        conn.close()
        
        dialog.open = False
        show_toast("Producto eliminado", WARNING_COLOR)
        page.update()
        load_products()

    def open_info_modal(prod):
        m_name = ft.TextField(label="Nombre", value=prod["name"])
        m_desc = ft.TextField(label="Descripción", value=prod["description"])
        m_price_buy = ft.TextField(label="Precio de compra", value=str(prod["price_buy"]))
        m_price_sell = ft.TextField(label="Precio de venta", value=str(prod["price_sell"]))
        m_stock = ft.TextField(label="Stock", value=str(prod["stock"]))
        m_stock_min = ft.TextField(label="Stock mínimo", value=str(prod["stock_min"]))
        m_cat = ft.Dropdown(
            label="Categoría",
            value=prod["category"],
            options=[ft.dropdown.Option("General"), ft.dropdown.Option("Alimentos"), ft.dropdown.Option("Electrónica")]
        )
        m_status = ft.Switch(label="Estado", value=bool(prod["status"]), active_color=PRIMARY_COLOR)

        def save_edit(e):
            if not m_name.value or not m_price_sell.value:
                show_toast("Nombre y precio de venta son obligatorios", DANGER_COLOR)
                return
                
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE products 
                    SET name=?, description=?, price_buy=?, price_sell=?, stock=?, stock_min=?, category=?, status=?
                    WHERE id=?
                ''', (
                    m_name.value, m_desc.value, float(m_price_buy.value or 0), float(m_price_sell.value),
                    float(m_stock.value or 0), float(m_stock_min.value or 0), m_cat.value, 
                    1 if m_status.value else 0, prod["id"]
                ))
                conn.commit()
                dialog.open = False
                show_toast("Producto actualizado", SUCCESS_COLOR)
                page.update()
                load_products()
            except Exception as ex:
                show_toast(f"Error: {ex}", DANGER_COLOR)
            finally:
                conn.close()

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text("Info producto", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: close_dialog(dialog))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                m_name, m_desc, m_price_buy, m_price_sell, m_stock, m_stock_min, m_cat,
                m_status
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=350),
            actions=[
                ft.TextButton("Eliminar", icon=ft.Icons.DELETE, style=ft.ButtonStyle(color=DANGER_COLOR), on_click=lambda _: delete_prod(prod["id"], dialog)),
                ft.Button("Actualizar", bgcolor=PRIMARY_COLOR, color="white", on_click=save_edit)
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
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
            tf_price_buy,
            tf_price_sell,
            tf_stock_actual,
            tf_stock_min,
            dd_category,
            sw_status,
            ft.Text("El id del producto y el código se generan automáticamente", size=11, color=TEXT_SECONDARY, italic=True),
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True, on_click=reset_fields),
                ft.Button("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=register_product)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    data_panel = ft.Container(
        expand=6,
        content=ft.Column([
            ft.Text("Productos", weight=ft.FontWeight.BOLD, size=24),
            search_bar,
            ft.Container(
                content=product_grid,
                bgcolor=SURFACE_COLOR, 
                border_radius=BORDER_RADIUS, 
                padding=15, 
                expand=True
            )
        ])
    )

    load_products()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([create_form, data_panel], spacing=20)
    )
