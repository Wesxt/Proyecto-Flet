import flet as ft
from core.colors import *
from core.database import get_connection

def InventarioView(page: ft.Page):
    """
    Dashboard de Inventario con CRUD real conectado a la DB.
    """
    
    # --- Referencias a Controles ---
    table_alerts = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Item")), 
            ft.DataColumn(label=ft.Text("Stock actual")), 
            ft.DataColumn(label=ft.Text("Min.")), 
            ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[]
    )
    
    table_items = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Item")), 
            ft.DataColumn(label=ft.Text("Compra")), 
            ft.DataColumn(label=ft.Text("Venta")),
            ft.DataColumn(label=ft.Text("Stock")), 
            ft.DataColumn(label=ft.Text("Min.")), 
            ft.DataColumn(label=ft.Text("Acciones"))
        ],
        rows=[]
    )

    # Definimos search_items aquí para que load_data pueda acceder a él
    search_items = ft.TextField(
        hint_text="Buscar Item", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        border_radius=10,
        expand=True,
    )

    # --- Lógica de Base de Datos ---

    def load_data(e=None):
        search_term = search_items.value.lower() if search_items.value else ""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Filtro de búsqueda para items generales
        query = "SELECT * FROM products WHERE status = 1"
        params = []
        if search_term:
            query += " AND (name LIKE ?)"
            params = [f"%{search_term}%"]
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        table_items.rows.clear()
        for p in products:
            table_items.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p["name"])),
                    ft.DataCell(ft.Text(f"${p['price_buy']:.2f}")),
                    ft.DataCell(ft.Text(f"${p['price_sell']:.2f}")),
                    ft.DataCell(ft.Text(str(p["stock"]))),
                    ft.DataCell(ft.Text(str(p["stock_min"]))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            ft.Icons.CANCEL_OUTLINED, 
                            icon_color=DANGER_COLOR,
                            on_click=lambda _, pid=p["id"]: delete_item(pid)
                        ), 
                        ft.IconButton(
                            ft.Icons.SETTINGS_OUTLINED, 
                            icon_color=SECONDARY_COLOR,
                            on_click=lambda _, prod=p: open_item_dialog(is_edit=True, item_data=prod)
                        )
                    ]))
                ])
            )

        # Cargar Alertas (Stock <= Stock Min)
        cursor.execute("SELECT * FROM products WHERE status = 1 AND stock <= stock_min")
        alerts = cursor.fetchall()
        table_alerts.rows.clear()
        for a in alerts:
            table_alerts.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(a["name"])),
                    ft.DataCell(ft.Text(str(a["stock"]), color=DANGER_COLOR, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(str(a["stock_min"]))),
                    ft.DataCell(ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color=SUCCESS_COLOR))
                ])
            )
        
        conn.close()
        page.update()

    # Configurar el evento de búsqueda
    search_items.on_change = load_data

    def delete_item(product_id):
        def confirm_delete(e):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET status = 0 WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            page.pop_dialog()
            load_data()
            page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar este item del inventario?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(confirm_dialog)),
                ft.ElevatedButton("Eliminar", bgcolor=DANGER_COLOR, color="white", on_click=confirm_delete)
            ]
        )
        page.show_dialog(confirm_dialog)
        page.update()

    def save_item(is_edit, product_id, data):
        conn = get_connection()
        cursor = conn.cursor()
        
        if is_edit:
            cursor.execute('''
                UPDATE products 
                SET name=?, price_buy=?, price_sell=?, stock=?, stock_min=?, in_limit=?, out_limit=?, adj_limit=?
                WHERE id=?
            ''', (data['name'], data['price_buy'], data['price_sell'], data['stock'], data['stock_min'], 
                  data['in_limit'], data['out_limit'], data['adj_limit'], product_id))
        else:
            cursor.execute('''
                INSERT INTO products (name, price_buy, price_sell, stock, stock_min, in_limit, out_limit, adj_limit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (data['name'], data['price_buy'], data['price_sell'], data['stock'], data['stock_min'],
                  data['in_limit'], data['out_limit'], data['adj_limit']))
        
        conn.commit()
        conn.close()
        load_data()

    # --- UI Components ---

    config_min_stock_val = ft.Text("10", color="white", weight=ft.FontWeight.BOLD)
    min_stock_container = ft.Container(
        content=ft.Row([
            ft.Text("Limite mínimo de stock", size=14, color=TEXT_PRIMARY),
            ft.Container(
                content=config_min_stock_val,
                padding=ft.Padding.symmetric(horizontal=15, vertical=5),
                border=ft.Border.all(1, SECONDARY_COLOR),
                border_radius=5,
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        padding=10,
        bgcolor=SURFACE_COLOR,
        border_radius=ft.BorderRadius.only(bottom_left=10, bottom_right=10),
        border=ft.Border.only(top=ft.BorderSide(1, DIVIDER_COLOR))
    )

    def open_item_dialog(is_edit=False, item_data=None):
        tf_name = ft.TextField(label="Nombre del Item", value=item_data["name"] if item_data else "", border_color=PRIMARY_COLOR)
        tf_price_buy = ft.TextField(label="Precio de compra", value=str(item_data["price_buy"]) if item_data else "", border_color=PRIMARY_COLOR)
        tf_price_sell = ft.TextField(label="Precio de venta", value=str(item_data["price_sell"]) if item_data else "", border_color=PRIMARY_COLOR)
        tf_stock = ft.TextField(label="Stock", value=str(item_data["stock"]) if item_data else "", border_color=PRIMARY_COLOR)
        tf_stock_min = ft.TextField(label="Limite mínimo de stock", value=str(item_data["stock_min"]) if item_data else "10", border_color=PRIMARY_COLOR)
        
        tf_in_limit = ft.TextField(label="Entradas restantes", value=str(item_data["in_limit"]) if item_data else "10", border_color=TEXT_SECONDARY)
        tf_out_limit = ft.TextField(label="Salidas restantes", value=str(item_data["out_limit"]) if item_data else "10", border_color=TEXT_SECONDARY)
        tf_adj_limit = ft.TextField(label="Ajustes restantes", value=str(item_data["adj_limit"]) if item_data else "10", border_color=TEXT_SECONDARY)

        def on_save_click(e):
            try:
                data = {
                    'name': tf_name.value,
                    'price_buy': float(tf_price_buy.value),
                    'price_sell': float(tf_price_sell.value),
                    'stock': float(tf_stock.value),
                    'stock_min': float(tf_stock_min.value),
                    'in_limit': int(tf_in_limit.value),
                    'out_limit': int(tf_out_limit.value),
                    'adj_limit': int(tf_adj_limit.value)
                }
                save_item(is_edit, item_data["id"] if item_data else None, data)
                close_dialog(dialog)
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingrese valores numéricos válidos"), bgcolor=DANGER_COLOR)
                page.snack_bar.open = True
                page.update()

        title = "Información y config de alerta" if is_edit else "Crear Inventario"
        button_text = "Editar" if is_edit else "Crear"

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text(title, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: close_dialog(dialog))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Container(
                width=600,
                content=ft.Row([
                    ft.Column([
                        tf_name, tf_price_buy, tf_price_sell, tf_stock,
                        ft.Text("Alerta", weight=ft.FontWeight.BOLD, color=SECONDARY_COLOR),
                        tf_stock_min,
                        ft.Container(height=10),
                        ft.Button(
                            button_text, 
                            bgcolor=PRIMARY_COLOR, 
                            color=TEXT_PRIMARY, 
                            width=200,
                            height=45,
                            on_click=on_save_click
                        )
                    ], tight=True, width=280, spacing=15),
                    ft.Container(
                        padding=20, border=ft.Border.all(1, DIVIDER_COLOR), border_radius=10,
                        content=ft.Column([
                            ft.Text("Restricciones de movimiento", weight=ft.FontWeight.BOLD),
                            tf_in_limit, tf_out_limit, tf_adj_limit,
                        ], tight=True, width=260, spacing=15)
                    )
                ], spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
            ),
            bgcolor=SURFACE_COLOR,
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
        )
        page.show_dialog(dialog)
        page.update()

    def close_dialog(dialog):
        page.pop_dialog()
        page.update()

    # --- Layout Panels ---
    left_panel = ft.Container(
        expand=True,
        content=ft.Column(
            controls = [
            ft.Text("Alertas de Stock", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([table_alerts], scroll=ft.ScrollMode.AUTO),
                bgcolor=SURFACE_COLOR, 
                border_radius=ft.BorderRadius.only(top_left=10, top_right=10), 
                padding=10,
                expand=True,
                alignment=ft.Alignment.TOP_CENTER
                ),
            min_stock_container
        ], spacing=10)
    )

    right_panel = ft.Container(
        expand=True,
        content=ft.Column(
            controls = [
            ft.Row([search_items]),
            ft.Container(
                content=ft.Column([table_items], scroll=ft.ScrollMode.AUTO),
                bgcolor=SURFACE_COLOR, 
                border_radius=10, 
                padding=10, 
                expand=True,
                alignment=ft.Alignment.TOP_CENTER
            )
        ])
    )

    header = ft.Row([
        ft.Container(width=150),
        ft.Text("Inventario", size=28, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
        ft.Button(
            "Crear Inventario", 
            icon=ft.Icons.ADD, 
            bgcolor=BACKGROUND_COLOR, 
            color=TEXT_PRIMARY,
            on_click=lambda _: open_item_dialog(is_edit=False),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Inicializar datos
    load_data()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
            header,
            ft.Container(height=20),
            ft.Row([
                left_panel, 
                ft.VerticalDivider(width=1, color=DIVIDER_COLOR), 
                right_panel
            ], expand=True, spacing=30)
        ])
    )
