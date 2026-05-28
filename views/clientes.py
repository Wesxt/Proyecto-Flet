import flet as ft
from core.colors import *
from controllers.clientes_controller import ClientesController

class ClientesView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = ClientesController(self)
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Formulario de Registro ---
        self.tf_name = ft.TextField(label="Nombre y apellido", expand=True)
        self.dd_doc_type = ft.Dropdown(
            label="Tipo de documento",
            options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT"), ft.dropdown.Option("Pasaporte")],
            width=200,
            value="Cédula de ciudadanía"
        )
        self.tf_doc_num = ft.TextField(label="Número de documento", expand=True)
        self.tf_phone = ft.TextField(label="Teléfono (Opcional)", expand=True)
        self.tf_email = ft.TextField(label="E-mail (Opcional)", expand=True)
        self.tf_address = ft.TextField(label="Dirección (Opcional)", expand=True)

        # --- Tabla de Clientes ---
        self.search_bar = ft.TextField(
            hint_text="Buscar Cliente...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            on_change=lambda _: self.load_data()
        )
        
        self.table = ft.DataTable(
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

        registration_form = ft.Container(
            expand=4, bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
            content=ft.Column([
                ft.Text("Registrar cliente frecuente", weight=ft.FontWeight.BOLD, size=18),
                self.tf_name,
                ft.Row([self.dd_doc_type, self.tf_doc_num]),
                self.tf_phone,
                self.tf_email,
                self.tf_address,
                ft.Row([
                    ft.OutlinedButton("Restablecer", expand=True, on_click=self.reset_fields),
                    ft.Button("Registrar", bgcolor=PRIMARY_COLOR, color="white", expand=True, on_click=self.register_client)
                ], spacing=10)
            ], scroll=ft.ScrollMode.AUTO)
        )

        data_panel = ft.Container(
            expand=6,
            content=ft.Column([
                ft.Row([
                    ft.Text("Clientes frecuentes", weight=ft.FontWeight.BOLD, size=24, expand=True),
                    self.search_bar
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column([self.table], scroll=ft.ScrollMode.AUTO),
                    bgcolor=SURFACE_COLOR, 
                    border_radius=BORDER_RADIUS, 
                    padding=10, 
                    expand=True,
                    alignment=ft.Alignment.TOP_CENTER
                )
            ])
        )

        self.content = ft.Row([registration_form, data_panel], spacing=20)

    def load_data(self):
        clients = self.controller.get_clients(self.search_bar.value)
        self.table.rows.clear()
        
        for c in clients:
            last_p = c.last_purchase[:10] if c.last_purchase else "N/A"
            self.table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(c.fullname)),
                    ft.DataCell(ft.Text(c.doc_type if c.doc_type else "N/A")),
                    ft.DataCell(ft.Text(c.doc_num if c.doc_num else "N/A")),
                    ft.DataCell(ft.Text(last_p)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=DANGER_COLOR, on_click=lambda _, cid=c.id: self.delete_client(cid)),
                        ft.IconButton(ft.Icons.EXPAND_CIRCLE_DOWN_OUTLINED, icon_color=PRIMARY_COLOR, on_click=lambda _, client_data=c: self.open_info_modal(client_data)),
                    ]))
                ])
            )
        self.page_ref.update()

    def show_toast(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.overlay.append(snack)
        snack.open = True
        self.page_ref.update()

    def reset_fields(self, e=None):
        self.tf_name.value = ""
        self.tf_doc_num.value = ""
        self.tf_phone.value = ""
        self.tf_email.value = ""
        self.tf_address.value = ""
        self.dd_doc_type.value = "Cédula de ciudadanía"
        self.page_ref.update()

    def register_client(self, e):
        success, message = self.controller.register_client(
            self.tf_name.value, self.dd_doc_type.value, self.tf_doc_num.value,
            self.tf_phone.value, self.tf_email.value, self.tf_address.value
        )
        self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
        if success:
            self.reset_fields()
            self.load_data()

    def delete_client(self, client_id):
        def confirm_delete(e):
            success, message = self.controller.delete_client(client_id)
            self.page_ref.pop_dialog()
            self.show_toast(message, WARNING_COLOR if success else DANGER_COLOR)
            if success:
                self.load_data()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de que desea eliminar a este cliente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.close_dialog(confirm_dialog)),
                ft.Button("Eliminar", bgcolor=DANGER_COLOR, color="white", on_click=confirm_delete)
            ]
        )
        self.page_ref.show_dialog(confirm_dialog)
        self.page_ref.update()

    def open_info_modal(self, client_data):
        m_name = ft.TextField(label="Nombre y apellido", value=client_data.fullname, border_color=PRIMARY_COLOR)
        m_doc_type = ft.Dropdown(
            label="Tipo de documento", 
            value=client_data.doc_type if client_data.doc_type else "Cédula de ciudadanía", 
            options=[ft.dropdown.Option("Cédula de ciudadanía"), ft.dropdown.Option("NIT"), ft.dropdown.Option("Pasaporte")]
        )
        m_doc_num = ft.TextField(label="Número de documento", value=client_data.doc_num)
        m_phone = ft.TextField(label="Teléfono", value=client_data.phone)
        m_email = ft.TextField(label="E-mail", value=client_data.email)
        m_address = ft.TextField(label="Dirección", value=client_data.address)

        def update_client(e):
            success, message = self.controller.update_client(
                client_data.id, m_name.value, m_doc_type.value, m_doc_num.value,
                m_phone.value, m_email.value, m_address.value
            )
            self.close_dialog(dialog)
            self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
            if success:
                self.load_data()

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Text("Información adicional", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: self.close_dialog(dialog))
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
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def close_dialog(self, dialog):
        self.page_ref.pop_dialog()
        self.page_ref.update()
