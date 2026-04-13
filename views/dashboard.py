import flet as ft
from core.colors import *

def DashboardView(page: ft.Page):
    """
    Panel de Control - Rol Administrador (Imagen 6).
    Incluye resúmenes de ventas, reportes y alertas de stock crítico.
    """
    
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

    # Widgets de Información (Imagen 6)
    metrics_row = ft.Row([
        metric_card("Ingresos Hoy", "$ 450,000", ft.Icons.ATTACH_MONEY, SUCCESS_COLOR),
        metric_card("Alertas Stock", "5 Items", ft.Icons.WARNING_AMBER_ROUNDED, WARNING_COLOR),
        metric_card("Ventas Realizadas", "28", ft.Icons.SHOPPING_CART_CHECKOUT, PRIMARY_COLOR),
    ], spacing=20)

    # Secciones de Resumen (Imagen 6)
    def summary_section(title, content):
        return ft.Container(
            bgcolor=SURFACE_COLOR, padding=20, border_radius=BORDER_RADIUS,
            expand=True, content=ft.Column([
                ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                ft.Divider(color=DIVIDER_COLOR),
                content
            ])
        )

    # Listas simuladas para los widgets
    recent_sales = ft.Column([
        ft.ListTile(title=ft.Text("Venta #123", size=14), subtitle=ft.Text("Hace 5 mins - $15,000", size=12), leading=ft.Icon(ft.Icons.RECEIPT, color=PRIMARY_COLOR)),
        ft.ListTile(title=ft.Text("Venta #122", size=14), subtitle=ft.Text("Hace 15 mins - $8,500", size=12), leading=ft.Icon(ft.Icons.RECEIPT, color=PRIMARY_COLOR)),
    ])

    stock_alerts = ft.Column([
        ft.ListTile(title=ft.Text("Agua 500ml", size=14), subtitle=ft.Text("Stock: 5 (Min: 10)", size=12), leading=ft.Icon(ft.Icons.ERROR_OUTLINE, color=DANGER_COLOR)),
        ft.ListTile(title=ft.Text("Papas Fritas", size=14), subtitle=ft.Text("Stock: 2 (Min: 5)", size=12), leading=ft.Icon(ft.Icons.ERROR_OUTLINE, color=DANGER_COLOR)),
    ])

    return ft.Container(
        expand=True, padding=30, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
            ft.Text("Dashboard de Gestión", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Resumen general de salud del negocio y métricas clave.", color=TEXT_SECONDARY),
            ft.Divider(height=40, color="transparent"),
            metrics_row,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                summary_section("Últimas Ventas", recent_sales),
                summary_section("Alertas de Stock Crítico", stock_alerts),
            ], spacing=20, expand=True)
        ], scroll=ft.ScrollMode.AUTO)
    )
