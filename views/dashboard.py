import flet as ft
from core.colors import *
from controllers.dashboard_controller import DashboardController

class DashboardView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=30,
            bgcolor=BACKGROUND_COLOR
        )
        self.page_ref = page
        self.controller = DashboardController(self)
        
        self.build_ui()

    def build_ui(self):
        # Fetch metrics and lists from controller
        data = self.controller.get_dashboard_data()
        
        # --- UI Components ---
        def metric_card(title, value, icon, color):
            return ft.Container(
                bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
                expand=True, shadow=ft.BoxShadow(blur_radius=10, color="#33000000"),
                content=ft.Row([
                    ft.Container(ft.Icon(icon, color=color, size=30), bgcolor=f"#1A{color[1:]}", padding=10, shape=ft.BoxShape.CIRCLE),
                    ft.Column([
                        ft.Text(title, size=14, color=TEXT_SECONDARY),
                        ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
                    ], spacing=2)
                ])
            )

        # Métricas Reales
        metrics_row = ft.Row([
            metric_card("Ingresos Hoy", f"$ {data['today_revenue']:,.0f}", ft.Icons.ATTACH_MONEY, SUCCESS_COLOR),
            metric_card("Alertas Stock", f"{data['stock_alerts_count']} Items", ft.Icons.WARNING_AMBER_ROUNDED, WARNING_COLOR),
            metric_card("Ventas Hoy", str(data['today_sales_count']), ft.Icons.SHOPPING_CART_CHECKOUT, PRIMARY_COLOR),
        ], spacing=20)

        def summary_section(title, content):
            return ft.Container(
                bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
                expand=True, content=ft.Column([
                    ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                    ft.Divider(color=DIVIDER_COLOR),
                    content
                ])
            )

        # Lista de Ventas Recientes Dinámica
        recent_sales_list = ft.Column(spacing=10)
        if data['recent_sales']:
            for sale in data['recent_sales']:
                client = sale.client_name if sale.client_name else "Cliente General"
                recent_sales_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"Venta #{sale.id} - {client}", size=14),
                        subtitle=ft.Text(f"{sale.date} - ${sale.total:,.2f}", size=12),
                        leading=ft.Icon(ft.Icons.RECEIPT, color=PRIMARY_COLOR)
                    )
                )
        else:
            recent_sales_list.controls.append(ft.Text("No hay ventas registradas recientemente.", color=TEXT_SECONDARY, italic=True))

        # Lista de Alertas de Stock Dinámica
        stock_alerts_list = ft.Column(spacing=10)
        if data['stock_alerts']:
            for item in data['stock_alerts']:
                stock_alerts_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(item.name, size=14),
                        subtitle=ft.Text(f"Stock actual: {item.stock} (Mínimo: {item.stock_min})", size=12),
                        leading=ft.Icon(ft.Icons.ERROR_OUTLINE, color=DANGER_COLOR)
                    )
                )
        else:
            stock_alerts_list.controls.append(ft.Text("Todo el stock está dentro de los niveles normales.", color=SUCCESS_COLOR, italic=True))

        self.content = ft.Column([
            ft.Text("Dashboard de Gestión", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Resumen en tiempo real del estado del negocio.", color=TEXT_SECONDARY),
            ft.Divider(height=40, color="transparent"),
            metrics_row,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                summary_section("Últimas Ventas", recent_sales_list),
                summary_section("Alertas de Stock Crítico", stock_alerts_list),
            ], spacing=20, expand=True)
        ], scroll=ft.ScrollMode.AUTO)
