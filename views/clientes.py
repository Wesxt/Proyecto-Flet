import flet as ft
from core.colors import *
from core.database import get_connection

def ClientesView(page: ft.Page):
    """
    Gestión de Clientes Frecuentes con CRUD en base de datos.
    """
    
    # --- Formulario de Registro ---
    tf_name = ft.TextField(label="Nombre y apellido", expand=True)
    dd_doc_type = ft.Dropdown(
        label="Tipo de documento",
        options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT"), ft.dropdown.Option("Pasaporte")],
        width=200,
        value="Cédula de ciudadanía"
    )
    tf_doc_num = ft.TextField(label="Número de documento", expand=True)
    tf_phone = ft.TextField(label="Teléfono (Opcional)", expand=True)
    tf_email = ft.TextField(label="E-mail (Opcional)", expand=True)
    tf_address = ft.TextField(label="Dirección (Opcional)", expand=True)

    def reset_fields(e=None):
        tf_name.value = ""
        tf_doc_num.value = ""
        tf_phone.value = ""
        tf_email.value = ""
        tf_address.value = ""
        dd_doc_type.value = "Cédula de ciudadanía"
        page.update()

    def show_toast(text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def load_clients():
        search_term = search_bar.value.lower() if search_bar.value else ""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtenemos clientes y su última compra
        query = '''
            SELECT c.*, MAX(s.date) as last_purchase 
            FROM clients c
            LEFT JOIN sales s ON c.id = s.client_id
            WHERE c.fullname LIKE ? OR c.doc_num LIKE ?
            GROUP BY c.id
        '''
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        clients = cursor.fetchall()
        conn.close()

        table.rows.clear()
        for c in clients:
            last_p = c["last_purchase"][:10] if c["last_purchase"] else "N/A"
            table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(c["fullname"])),
                    ft.DataCell(ft.Text(c["doc_type"] if c["doc_type"] else "N/A")),
                    ft.DataCell(ft.Text(c["doc_num"] if c["doc_num"] else "N/A")),
                    ft.DataCell(ft.Text(last_p)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR, on_click=lambda _, cid=c["id"]: delete_client(cid)),
                        ft.IconButton(ft.Icons.EXPAND_CIRCLE_DOWN_OUTLINED, icon_color=PRIMARY_COLOR, on_click=lambda _, client_data=c: open_info_modal(client_data)),
                    ]))
                ])
            )
        page.update()

    def register_client(e):
        if not tf_name.value or not tf_doc_num.value:
            show_toast("Nombre y número de documento son obligatorios", DANGER_COLOR)
            return

        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clients (fullname, doc_type, doc_num, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tf_name.value, dd_doc_type.value, tf_doc_num.value, tf_phone.value, tf_email.value, tf_address.value))
        
        conn.commit()
        conn.close()
        
        show_toast("Cliente registrado con éxito", SUCCESS_COLOR)
        reset_fields()
        load_clients()

    def delete_client(client_id):
        def confirm_delete(e):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            conn.close()
            confirm_dialog.open = False
            page.update()
            show_toast("Cliente eliminado", WARNING_COLOR)
            load_clients()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar a este cliente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(confirm_dialog)),
                ft.Button("Eliminar", bgcolor=DANGER_COLOR, color="white", on_click=confirm_delete)
            ]
        )
        page.overlay.append(confirm_dialog)
        confirm_dialog.open = True
        page.update()

    def open_info_modal(client_data):
        # Campos del modal
        m_name = ft.TextField(label="Nombre y apellido", value=client_data["fullname"], border_color=PRIMARY_COLOR)
        m_doc_type = ft.Dropdown(
            label="Tipo de documento", 
            value=client_data["doc_type"] if client_data["doc_type"] else "Cédula de ciudadanía", 
            options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT"), ft.dropdown.Option("Pasaporte")]
        )
        m_doc_num = ft.TextField(label="Número de documento", value=client_data["doc_num"])
        m_phone = ft.TextField(label="Teléfono", value=client_data["phone"])
        m_email = ft.TextField(label="E-mail", value=client_data["email"])
        m_address = ft.TextField(label="Dirección", value=client_data["address"])

        def update_client(e):
            if not m_name.value or not m_doc_num.value:
                show_toast("Nombre y número de documento son obligatorios", DANGER_COLOR)
                return
                
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE clients SET fullname=?, doc_type=?, doc_num=?, phone=?, email=?, address=?
                WHERE id=?
            ''', (m_name.value, m_doc_type.value, m_doc_num.value, m_phone.value, m_email.value, m_address.value, client_data["id"]))
            conn.commit()
            conn.close()
            
            close_dialog(dialog)
            show_toast("Datos del cliente actualizados", SUCCESS_COLOR)
            load_clients()

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text("Información adicional", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: close_dialog(dialog))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                m_name,
                m_doc_type,
                m_doc_num,
                m_phone,
                m_email,
                m_address,
            ], tight=True, scroll=ft.ScrollMode.AUTO, width=400),
            actions=[
                ft.Button("Actualizar", bgcolor=PRIMARY_COLOR, color="white", on_click=update_client)
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # --- Tabla de Clientes ---
    search_bar = ft.TextField(
        hint_text="Buscar Cliente...", 
        prefix_icon=ft.Icons.SEARCH, 
        bgcolor=SURFACE_COLOR,
        on_change=lambda _: load_clients()
    )
    
    table = ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("Nombre")),
            ft.DataColumn(label=ft.Text("Tipo de doc")),
            ft.DataColumn(label=ft.Text("Num de doc")),
            ft.DataColumn(label=ft.Text("Última compra")),
            ft.DataColumn(label=ft.Text("Acciones")),
        ],
        rows=[],
        expand=True
    )

    # --- Layout ---
    registration_form = ft.Container(
        expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
        content=ft.Column([
            ft.Text("Registrar cliente frecuente", weight=ft.FontWeight.BOLD, size=18),
            tf_name,
            ft.Row([dd_doc_type, tf_doc_num]),
            tf_phone,
            tf_email,
            tf_address,
            ft.Row([
                ft.OutlinedButton("Restablecer", expand=True, on_click=reset_fields),
                ft.Button("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=register_client)
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    data_panel = ft.Container(
        expand=6,
        content=ft.Column([
            ft.Row([
                ft.Text("Clientes frecuentes", weight=ft.FontWeight.BOLD, size=24, expand=True),
                search_bar
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Column([table], scroll=ft.ScrollMode.AUTO),
                bgcolor=SURFACE_COLOR, 
                border_radius=BORDER_RADIUS, 
                padding=10, 
                expand=True,
                alignment=ft.Alignment.TOP_CENTER
            )
        ])
    )

    load_clients()

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([registration_form, data_panel], spacing=20)
    )
