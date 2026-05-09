import flet as ft
from core.colors import *
from core.database import get_connection
import datetime

def BillingView(page: ft.Page, navigate_to_pos, state):
    """
    Módulo de Facturación (Imagen 7).
    Conectado a la base de datos para Clientes y Registro de Ventas.
    """
    
    # --- Estado Global ---
    cart_items = state.cart_items
    all_clients = []
    
    # Totales del Carrito
    subtotal = sum(item['price'] for item in cart_items)
    iva = subtotal * 0.19
    total = subtotal + iva
    items_count = len(cart_items)

    def show_toast(text, color):
        sb = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.overlay.append(sb)
        sb.open = True
        page.update()

    # --- Componentes Izquierda (Búsqueda de Clientes) ---
    btn_back = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=TEXT_PRIMARY,
        tooltip="Volver a los productos en carrito",
        on_click=lambda _: navigate_to_pos()
    )
    
    search_client = ft.TextField(
        hint_text="Buscar Cliente", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR, 
        height=45,
        on_change=lambda _: filter_clients()
    )
    
    client_table = ft.DataTable(
        columns=[ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD)), ft.DataColumn(label=ft.Text("Ultima compra", weight=ft.FontWeight.BOLD))],
        rows=[],
        expand=True,
        heading_row_color=BACKGROUND_COLOR,
        show_bottom_border=True
    )

    def load_clients_from_db():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, MAX(s.date) as last_purchase 
            FROM clients c
            LEFT JOIN sales s ON c.id = s.client_id
            GROUP BY c.id
        ''')
        nonlocal all_clients
        all_clients = cursor.fetchall()
        conn.close()
        filter_clients()

    def filter_clients():
        term = search_client.value.lower() if search_client.value else ""
        client_table.rows.clear()
        
        for c in all_clients:
            if term in c['fullname'].lower() or (c['doc_num'] and term in c['doc_num']):
                last_p = c["last_purchase"][:10] if c["last_purchase"] else "N/A"
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c['fullname'])), 
                        ft.DataCell(ft.Text(last_p))
                    ],
                    on_select_change=lambda e, client=c: select_client(client)
                )
                client_table.rows.append(row)
        page.update()

    def select_client(client):
        tf_name.value = client['fullname']
        if client['doc_type']: dd_doc_type.value = client['doc_type']
        if client['doc_num']: tf_doc_num.value = client['doc_num']
        sw_register_client.value = False
        sw_register_client.disabled = True
        page.update()

    info_text = ft.Text(
        "Esto sirve como plantilla para completar más rápido la facturación con datos no sensibles cuando se seleccione un cliente frecuente registrado y también para registrar su compra",
        color=DANGER_COLOR, size=12, italic=True
    )

    left_panel = ft.Container(
        expand=4,
        content=ft.Column([
            ft.Row([btn_back, search_client], expand=False),
            ft.Container(
                content=ft.Column([client_table], scroll=ft.ScrollMode.AUTO),
                bgcolor=SURFACE_COLOR, border_radius=10, border=ft.Border.all(1, DIVIDER_COLOR), expand=True
            ),
            info_text
        ])
    )

    # --- Componentes Derecha (Formulario Adaptativo) ---
    tf_name = ft.TextField(label="Nombre y apellido")
    dd_doc_type = ft.Dropdown(
        label="Tipo de documento",
        options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT")],
        value="Cédula de ciudadanía"
    )
    tf_doc_num = ft.TextField(label="Número de documento")
    
    # Campos de Tarjeta
    card_fields = ft.Column([
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

    cash_info = ft.Text("Si es efectivo no hay más datos que pedir sobre el método de pago", color=SUCCESS_COLOR, size=12, italic=True, visible=True)

    def on_payment_change(e):
        is_tarjeta = (e.control.value == "tarjeta")
        card_fields.visible = is_tarjeta
        cash_info.visible = not is_tarjeta
        page.update()

    payment_method = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="tarjeta", label="Tarjeta de credito/debito"),
            ft.Radio(value="efectivo", label="Efectivo"),
        ]),
        value="efectivo",
        on_change=on_payment_change
    )

    # Totales y Métricas
    now = datetime.datetime.now()
    metrics_panel = ft.Container(
        padding=10,
        content=ft.Row([
            ft.Column([
                ft.Text(f"Subtotal: $ {subtotal:.0f}", color=DANGER_COLOR, size=12),
                ft.Text(f"Descuento: -$ 0", color=DANGER_COLOR, size=12),
                ft.Text(f"IVA: $ {iva:.0f} (19%)", color=DANGER_COLOR, size=12),
                ft.Text(f"Total: $ {total:.0f}", color=DANGER_COLOR, weight=ft.FontWeight.BOLD),
            ]),
            ft.Column([
                ft.Text(f"Ítems: {items_count}", size=12),
                ft.Text(f"Fecha: {now.strftime('%d/%m/%Y')}", size=12),
                ft.Text(f"Hora: {now.strftime('%H:%M %p')}", size=12),
            ]),
            ft.Column([
                ft.Text(f"Codigo de Fac:", size=12),
                ft.Text(f"FAC-N/A", weight=ft.FontWeight.BOLD),
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    sw_register_client = ft.Switch(active_color=TEXT_PRIMARY)

    def reset_fields(e=None):
        tf_name.value = ""
        tf_doc_num.value = ""
        sw_register_client.value = False
        sw_register_client.disabled = False
        page.update()

    def process_billing(e):
        if not cart_items:
            show_toast("El carrito está vacío", DANGER_COLOR)
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Identificar o registrar cliente
            client_id = None
            if tf_name.value:
                # Comprobar si existe el cliente
                cursor.execute("SELECT id FROM clients WHERE doc_num = ? AND doc_type = ?", (tf_doc_num.value, dd_doc_type.value))
                existing_client = cursor.fetchone()
                
                if existing_client:
                    client_id = existing_client["id"]
                elif sw_register_client.value:
                    cursor.execute("INSERT INTO clients (fullname, doc_type, doc_num) VALUES (?, ?, ?)", 
                                  (tf_name.value, dd_doc_type.value, tf_doc_num.value))
                    client_id = cursor.lastrowid
                    
            # Obtener user_id
            cursor.execute("SELECT id FROM users WHERE username = ?", (state.username,))
            user_record = cursor.fetchone()
            user_id = user_record["id"] if user_record else None

            # Obtener metodo de pago
            metodo = payment_method.value.capitalize()

            # Insertar en sales
            cursor.execute("INSERT INTO sales (client_id, user_id, total, payment_method) VALUES (?, ?, ?, ?)", 
                          (client_id, user_id, total, metodo))
            sale_id = cursor.lastrowid

            # Insertar en sale_details
            for item in cart_items:
                cursor.execute("INSERT INTO sale_details (sale_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                              (sale_id, item['id'], 1, item['price']))

                # Reducir stock
                cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (item['id'],))

            conn.commit()
            show_toast("Factura registrada exitosamente", SUCCESS_COLOR)
            state.cart_items.clear()
            navigate_to_pos()

        except Exception as ex:
            conn.rollback()
            show_toast(f"Error al facturar: {str(ex)}", DANGER_COLOR)
        finally:
            conn.close()

    right_panel = ft.Container(
        expand=6,
        bgcolor=SURFACE_COLOR,
        padding=20,
        border_radius=15,
        border=ft.Border.all(1, DIVIDER_COLOR),
        content=ft.Column([
            ft.Text("Facturación", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            tf_name,
            ft.Row([dd_doc_type, tf_doc_num]),
            ft.Container(
                padding=10, border=ft.Border.all(1, DIVIDER_COLOR), border_radius=10,
                content=ft.Column([
                    ft.Text("Método de pago", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        payment_method,
                        ft.VerticalDivider(color=DIVIDER_COLOR),
                        ft.Column([card_fields, cash_info], expand=True)
                    ])
                ])
            ),
            ft.Divider(color=DIVIDER_COLOR),
            metrics_panel,
            ft.Row([
                ft.Text("Registrar nuevo cliente frecuente", size=14, color=TEXT_SECONDARY),
                sw_register_client
            ], alignment=ft.MainAxisAlignment.START),
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True, on_click=reset_fields),
                ft.Button("Facturar", bgcolor=TEXT_PRIMARY, color=BACKGROUND_COLOR, expand=True, on_click=process_billing)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    load_clients_from_db()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([left_panel, right_panel], spacing=30)
    )
