import flet as ft
from core.colors import *
from controllers.reportes_controller import ReportesController
import datetime

class ReportesView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=20,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = ReportesController(self)
        
        self.build_ui()
        self.load_data()

    def build_ui(self):
        # --- Referencias a Controles ---
        self.tf_start = ft.TextField(label="Fecha de inicio", hint_text="YYYY-MM-DD", expand=True, read_only=True)
        self.tf_end = ft.TextField(label="Fecha de corte", hint_text="YYYY-MM-DD", expand=True, read_only=True)
        
        # --- DatePickers Logic ---
        def handle_start_change(e):
            if date_picker_start.value:
                self.tf_start.value = date_picker_start.value.strftime("%Y-%m-%d")
            date_picker_start.open = False
            self.page_ref.update()

        def handle_end_change(e):
            if date_picker_end.value:
                self.tf_end.value = date_picker_end.value.strftime("%Y-%m-%d")
            date_picker_end.open = False
            self.page_ref.update()

        def handle_dismiss(e):
            e.control.open = False
            self.page_ref.update()

        date_picker_start = ft.DatePicker(
            on_change=handle_start_change,
            on_dismiss=handle_dismiss,
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        
        date_picker_end = ft.DatePicker(
            on_change=handle_end_change,
            on_dismiss=handle_dismiss,
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        self.page_ref.overlay.append(date_picker_start)
        self.page_ref.overlay.append(date_picker_end)

        def open_start_picker(e):
            date_picker_start.open = True
            self.page_ref.update()

        def open_end_picker(e):
            date_picker_end.open = True
            self.page_ref.update()

        self.tf_start.suffix_icon = ft.Icons.CALENDAR_MONTH
        self.tf_start.on_click = open_start_picker
        self.tf_end.suffix_icon = ft.Icons.CALENDAR_MONTH
        self.tf_end.on_click = open_end_picker

        self.table_reports = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Tipo de reporte")), 
                ft.DataColumn(label=ft.Text("Fecha de creación")), 
                ft.DataColumn(label=ft.Text("Periodo")),
                ft.DataColumn(label=ft.Text("Acciones"))
            ],
            rows=[],
            expand=True
        )

        self.search_bar = ft.TextField(
            hint_text="Buscar reporte...", 
            prefix_icon=ft.Icons.SEARCH, 
            bgcolor=SURFACE_COLOR,
            on_change=lambda _: self.load_data()
        )

        # Dropdown de Tipos de Reportes
        self.dd_report_type = ft.Dropdown(
            label="Tipo de Reporte",
            options=[
                ft.dropdown.Option("Ventas Generales"),
                ft.dropdown.Option("Ventas por Cajero"),
                ft.dropdown.Option("Ventas por Cliente"),
                ft.dropdown.Option("Inventario Actual"),
                ft.dropdown.Option("Inventario Bajo Stock"),
                ft.dropdown.Option("Productos Más Vendidos"),
                ft.dropdown.Option("Ganancias por Producto")
            ],
            value="Ventas Generales"
        )

        manual_panel = ft.Container(
            bgcolor=SURFACE_COLOR, padding=20, border_radius=10,
            content=ft.Column(
                controls=[
                    ft.Text("Generar manualmente reportes", weight=ft.FontWeight.BOLD, size=16),
                    self.dd_report_type,
                    ft.Row([self.tf_start, self.tf_end], spacing=10),
                    ft.Row([
                        ft.OutlinedButton("Restablecer", on_click=self.reset_fields),
                        ft.Button("Generar Reporte", bgcolor=PRIMARY_COLOR, color="white", on_click=self.generate_report)
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                ],
                spacing=20,
                alignment=ft.Alignment.TOP_CENTER
            )
        )

        # --- Main Layout ---
        self.content = ft.Row([
            ft.Column([manual_panel], expand=4, spacing=20),
            ft.VerticalDivider(width=1, color=DIVIDER_COLOR),
            ft.Column([
                ft.Text("Historial de Reportes", size=24, weight=ft.FontWeight.BOLD),
                self.search_bar,
                ft.Container(
                    content=ft.Column([self.table_reports], scroll=ft.ScrollMode.AUTO),
                    bgcolor=SURFACE_COLOR, 
                    border_radius=10, 
                    padding=10, 
                    expand=True, 
                    alignment=ft.Alignment.TOP_CENTER
                )
            ], expand=6)
        ], spacing=20)

    def load_data(self):
        reports = self.controller.get_reports()
        search_term = self.search_bar.value.lower() if self.search_bar.value else ""
        self.table_reports.rows.clear()
        
        for r in reports:
            if search_term and search_term not in r.type.lower():
                continue
                
            self.table_reports.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r.type)),
                    ft.DataCell(ft.Text(r.created_at[:10])),
                    ft.DataCell(ft.Text(f"{r.start_date} / {r.end_date}")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE, 
                            icon_color=DANGER_COLOR,
                            on_click=lambda _, rid=r.id: self.delete_report(rid)
                        ),
                        ft.IconButton(
                            ft.Icons.PICTURE_AS_PDF, 
                            icon_color=SECONDARY_COLOR,
                            on_click=lambda _, rid=r.id: self.export_report(rid)
                        )
                    ]))
                ])
            )
        self.page_ref.update()

    def generate_report(self, e):
        success, message = self.controller.generate_report(
            self.tf_start.value, self.tf_end.value, self.dd_report_type.value
        )
        self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)
        if success:
            self.load_data()

    def delete_report(self, report_id):
        success = self.controller.delete_report(report_id)
        if success:
            self.show_toast("Reporte eliminado", WARNING_COLOR)
            self.load_data()

    def export_report(self, report_id):
        success, message = self.controller.export_report(report_id)
        self.show_toast(message, SUCCESS_COLOR if success else DANGER_COLOR)

    def show_toast(self, text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        self.page_ref.overlay.append(snack)
        snack.open = True
        self.page_ref.update()

    def reset_fields(self, e=None):
        self.tf_start.value = ""
        self.tf_end.value = ""
        self.dd_report_type.value = "Ventas Generales"
        self.page_ref.update()
