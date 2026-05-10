import flet as ft
from core.colors import *
from core.database import init_db, get_connection

# Importación de vistas optimizadas según la documentación técnica
from views.login import LoginView
from views.dashboard import DashboardView
from views.pos import POSView
from views.billing import BillingView
from views.clientes import ClientesView
from views.productos import ProductosView
from views.inventario import InventarioView
from views.usuarios import UsuariosView
from views.reportes import ReportesView
from views.auditoria import AuditoriaView

class AppState:
    def __init__(self):
        self.role = None
        self.username = ""
        self.cart_items = []


def main(page: ft.Page):
    # Inicializar Base de Datos
    init_db()
    
    state = AppState()
    
    # --- Configuración de Ventana ---
    page.title = "POS ERP - Sistema de Gestión Comercial"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BACKGROUND_COLOR
    page.padding = 0
    page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"}
    page.theme = ft.Theme(font_family="Inter")

    # Contenedor dinámico para las vistas
    view_container = ft.Container(expand=True)
    root_container = ft.Container(expand=True)

    # --- Menú de Navegación Lateral ---
    def get_nav_destinations(role):
        if role == "Administrador":
            return [
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_OUTLINED, selected_icon=ft.Icons.PEOPLE, label="Usuarios"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG, label="Productos"),
                ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Inventario"),
                ft.NavigationRailDestination(icon=ft.Icons.BAR_CHART_OUTLINED, selected_icon=ft.Icons.BAR_CHART, label="Reportes"),
                ft.NavigationRailDestination(icon=ft.Icons.STAR_OUTLINE, selected_icon=ft.Icons.STAR, label="Clientes"),
                ft.NavigationRailDestination(icon=ft.Icons.LIST_ALT_OUTLINED, selected_icon=ft.Icons.LIST_ALT, label="Auditoría"),
            ]
        elif role == "Supervisor":
            return [
                ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Inventario"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG, label="Productos"),
                ft.NavigationRailDestination(icon=ft.Icons.LIST_ALT_OUTLINED, selected_icon=ft.Icons.LIST_ALT, label="Auditoría"),
            ]
        elif role == "Cajero":
            return [
                ft.NavigationRailDestination(icon=ft.Icons.POINT_OF_SALE, selected_icon=ft.Icons.POINT_OF_SALE, label="Punto de venta"),
                ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, selected_icon=ft.Icons.RECEIPT_LONG, label="Facturas"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG, label="Productos"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART_CHECKOUT, selected_icon=ft.Icons.SHOPPING_CART_CHECKOUT, label="Ventas"),
                ft.NavigationRailDestination(icon=ft.Icons.STAR_OUTLINE, selected_icon=ft.Icons.STAR, label="Clientes Frecuentes"),
            ]
        return []

    def on_nav_change(e):
        idx = e.control.selected_index
        role = state.role
        
        if role == "Administrador":
            views = ["dashboard", "usuarios", "productos", "inventario", "reportes", "clientes", "auditoria"]
            change_view(views[idx])
        elif role == "Supervisor":
            views = ["inventario", "productos", "auditoria"]
            change_view(views[idx])
        elif role == "Cajero":
            # Nota: "ventas" y "facturas" pueden apuntar a la misma vista temporalmente o a vistas existentes.
            # "pos" = Punto de Venta, "productos" = Productos, "clientes" = Clientes Frecuentes
            views = ["pos", "billing", "productos", "reportes", "clientes"]
            change_view(views[idx])

    # Rail de navegación lateral
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        bgcolor=SURFACE_COLOR,
        on_change=on_nav_change,
        group_alignment=-0.9,
    )

    # --- Seguridad en Cierre de Caja ---
    tf_close_pass = ft.TextField(label="Contraseña", password=True, width=250)
    error_text_modal = ft.Text("", color=DANGER_COLOR, size=12, visible=False)
    btn_confirm_close = ft.Button("Confirmar", bgcolor=DANGER_COLOR, color="white", disabled=True)

    def validate_close_pass(e):
        btn_confirm_close.disabled = len(tf_close_pass.value) < 1
        error_text_modal.visible = False
        page.update()

    tf_close_pass.on_change = validate_close_pass

    def close_cash_session(e, dialog):
        nonlocal view_container
        conn = get_connection()
        cursor = conn.cursor()
        # IMPORTANTE: Usar el username guardado en el estado
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (state.username, tf_close_pass.value))
        user = cursor.fetchone()
        conn.close()

        if user:
            state.role = None
            state.username = ""
            
            # Usar la API moderna de Flet para cerrar diálogos
            close_dialog()
            
            # En lugar de limpiar la página, actualizamos el root_container
            view_container = ft.Container(expand=True)
            root_container.content = view_container
            change_view("login")
            page.update()
        else:
            error_text_modal.value = "Contraseña incorrecta"
            error_text_modal.visible = True
            page.update()


    def show_close_cash_modal(e):
        # Calcular ventas del dia para el cierre
        conn = get_connection()
        cursor = conn.cursor()
        
        # Buscar el ID del usuario activo
        cursor.execute("SELECT id FROM users WHERE username = ?", (state.username,))
        u = cursor.fetchone()
        user_id = u["id"] if u else None
        
        # Ventas de hoy del usuario
        cursor.execute('''
            SELECT 
                COUNT(id) as total_ventas,
                SUM(CASE WHEN payment_method = 'Efectivo' THEN total ELSE 0 END) as total_efectivo,
                SUM(CASE WHEN payment_method = 'Tarjeta' THEN total ELSE 0 END) as total_tarjeta,
                SUM(total) as total_esperado
            FROM sales 
            WHERE user_id = ? AND date(date, 'localtime') = date('now', 'localtime')
        ''', (user_id,))
        res = cursor.fetchone()
        conn.close()

        total_ventas = res["total_ventas"] or 0
        t_efectivo = res["total_efectivo"] or 0
        t_tarjeta = res["total_tarjeta"] or 0
        t_esperado = res["total_esperado"] or 0

        # Mostramos los datos de Cierre de Caja (RF12)
        info_cierre = ft.Column([
            ft.Text(f"Total de ventas realizadas hoy: {total_ventas}"),
            ft.Text(f"Ventas en Efectivo: $ {t_efectivo:,.2f}"),
            ft.Text(f"Ventas con Tarjeta: $ {t_tarjeta:,.2f}"),
            ft.Text(f"Total Esperado en Caja: $ {t_esperado:,.2f}", weight=ft.FontWeight.BOLD, color=SUCCESS_COLOR),
            ft.Divider(color=DIVIDER_COLOR),
        ])

        dialog = ft.AlertDialog(
            title=ft.Text("Cierre de Sesión", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                info_cierre,
                ft.Text(f"Usuario activo: {state.username}", size=14, color=TEXT_SECONDARY),
                ft.Text("Ingrese su contraseña para terminar el turno:", size=14, color=TEXT_SECONDARY),
                tf_close_pass,
                error_text_modal
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                btn_confirm_close
            ],
            bgcolor=SURFACE_COLOR
        )
        btn_confirm_close.on_click = lambda e: close_cash_session(e, dialog)
        # Usar API moderna para abrir el diálogo
        page.show_dialog(dialog)
        tf_close_pass.value = ""
        error_text_modal.visible = False
        btn_confirm_close.disabled = True
        page.update()

    def close_dialog():
        page.pop_dialog()

    close_cash_btn = ft.Container(
        content=ft.TextButton(
            "Cerrar sesión",
            icon=ft.Icons.POWER_SETTINGS_NEW,
            style=ft.ButtonStyle(color=DANGER_COLOR),
            on_click=show_close_cash_modal
        ),
        padding=ft.Padding.only(bottom=20)
    )

    def change_view(name):
        view_container.content = None
        if name == "login":
            view_container.content = LoginView(page, on_login_success=login_success)
        elif name == "dashboard":
            view_container.content = DashboardView(page)
        elif name == "pos":
            view_container.content = POSView(page, lambda: change_view_from_internal("billing"), state)
        elif name == "billing":
            view_container.content = BillingView(page, lambda: change_view_from_internal("pos"), state)
        elif name == "clientes":
            view_container.content = ClientesView(page)
        elif name == "productos":
            view_container.content = ProductosView(page)
        elif name == "inventario":
            view_container.content = InventarioView(page)
        elif name == "usuarios":
            view_container.content = UsuariosView(page)
        elif name == "reportes":
            view_container.content = ReportesView(page)
        elif name == "auditoria":
            view_container.content = AuditoriaView(page)
        page.update()

    def change_view_from_internal(name):
        if state.role == "Cajero":
            rail.selected_index = 1
        rail.update()
        change_view(name)

    def login_success(role, username):
        state.role = role
        state.username = username
        
        rail.destinations = get_nav_destinations(role)
        rail.selected_index = 0
        rail.height=500
        rail.width=100
        
        main_layout = ft.Row(
            spacing=0,
            expand=True,
            controls=[
                ft.Container(
                    content=ft.Column([rail, ft.VerticalDivider(width=1, color=DIVIDER_COLOR), close_cash_btn], spacing=0, expand=True, width=100),
                    bgcolor=SURFACE_COLOR,
                    expand=False,
                ),
                ft.VerticalDivider(width=1, color=DIVIDER_COLOR),
                view_container
            ]
        )
        # Actualizamos el root_container en lugar de añadir a la página
        root_container.content = main_layout
        
        if role == "Administrador": change_view("dashboard")
        elif role == "Supervisor": change_view("inventario")
        else: change_view("pos")

    # Inicio de la App
    root_container.content = view_container
    page.add(root_container)
    change_view("login")

if __name__ == "__main__":
    ft.run(main)
