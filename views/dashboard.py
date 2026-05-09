import flet as ft
from core.colors import *
from core.database import get_connection
import datetime

def DashboardView(page: ft.Page):
    """
    Panel de Control funcional conectado a la base de datos.
    """
    
    # --- Datos de la Base de Datos ---
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Ingresos de hoy
    cursor.execute("SELECT SUM(total) FROM sales WHERE date(date) = date('now', 'localtime')")
    today_revenue = cursor.fetchone()[0] or 0
    
    # 2. Ventas realizadas hoy
    cursor.execute("SELECT COUNT(*) FROM sales WHERE date(date) = date('now', 'localtime')")
    today_sales_count = cursor.fetchone()[0]
    
    # 3. Cantidad de alertas de stock
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= stock_min AND status = 1")
    stock_alerts_count = cursor.fetchone()[0]
    
    # 4. Lista de últimas ventas
    cursor.execute('''
        SELECT s.id, s.total, s.date, c.fullname 
        FROM sales s 
        LEFT JOIN clients c ON s.client_id = c.id 
        ORDER BY s.date DESC LIMIT 5
    ''')
    recent_sales_data = cursor.fetchall()
    
    # 5. Lista de productos en alerta
    cursor.execute('''
        SELECT name, stock, stock_min 
        FROM products 
        WHERE stock <= stock_min AND status = 1 
        LIMIT 5
    ''')
    stock_alerts_data = cursor.fetchall()
    
    conn.close()

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
        metric_card("Ingresos Hoy", f"$ {today_revenue:,.0f}", ft.Icons.ATTACH_MONEY, SUCCESS_COLOR),
        metric_card("Alertas Stock", f"{stock_alerts_count} Items", ft.Icons.WARNING_AMBER_ROUNDED, WARNING_COLOR),
        metric_card("Ventas Hoy", str(today_sales_count), ft.Icons.SHOPPING_CART_CHECKOUT, PRIMARY_COLOR),
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
    if recent_sales_data:
        for sale in recent_sales_data:
            client = sale['fullname'] if sale['fullname'] else "Cliente General"
            recent_sales_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f"Venta #{sale['id']} - {client}", size=14),
                    subtitle=ft.Text(f"{sale['date']} - ${sale['total']:,.2f}", size=12),
                    leading=ft.Icon(ft.Icons.RECEIPT, color=PRIMARY_COLOR)
                )
            )
    else:
        recent_sales_list.controls.append(ft.Text("No hay ventas registradas recientemente.", color=TEXT_SECONDARY, italic=True))

    # Lista de Alertas de Stock Dinámica
    stock_alerts_list = ft.Column(spacing=10)
    if stock_alerts_data:
        for item in stock_alerts_data:
            stock_alerts_list.controls.append(
                ft.ListTile(
                    title=ft.Text(item['name'], size=14),
                    subtitle=ft.Text(f"Stock actual: {item['stock']} (Mínimo: {item['stock_min']})", size=12),
                    leading=ft.Icon(ft.Icons.ERROR_OUTLINE, color=DANGER_COLOR)
                )
            )
    else:
        stock_alerts_list.controls.append(ft.Text("Todo el stock está dentro de los niveles normales.", color=SUCCESS_COLOR, italic=True))

    return ft.Container(
        expand=True, padding=30, bgcolor=BACKGROUND_COLOR,
        content=ft.Column([
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
    )
