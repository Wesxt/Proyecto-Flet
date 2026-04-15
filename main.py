import flet as ft
from core.colors import *

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

# Integrantes del grupo:
#   Arnold Beleño Zuletta
#   Carlos Colón Cantillo
#   Jesús Santiago Díaz

def main(page: ft.Page):
    # --- Configuración de Ventana ---
    page.title = "POS ERP - Sistema de Gestión Comercial"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BACKGROUND_COLOR
    page.padding = 0
    page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"}
    page.theme = ft.Theme(font_family="Inter")

    # Contenedor dinámico para las vistas
    view_container = ft.Container(expand=True)

    # Estado global de la aplicación (Roles e interfaz)
    app_state = {
        "role": None, # Administrador, Supervisor, Cajero
        "user_name": ""
    }

    # --- Menú de Navegación Lateral (Arquitectura de Pantallas - Imagen 4) ---
    def get_nav_destinations(role):
        # El Administrador tiene acceso total (Imagen 6)
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
        # El Supervisor es un rol intermedio (Imagen 3) enfocado en inventario y auditoría
        elif role == "Supervisor":
            return [
                ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Inventario"),
                ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG, label="Productos"),
                ft.NavigationRailDestination(icon=ft.Icons.LIST_ALT_OUTLINED, selected_icon=ft.Icons.LIST_ALT, label="Auditoría"),
            ]
        # El Cajero está limitado a ventas y facturación (Imagen 5)
        elif role == "Cajero":
            return [
                ft.NavigationRailDestination(icon=ft.Icons.POINT_OF_SALE, selected_icon=ft.Icons.POINT_OF_SALE, label="Ventas"),
                ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, selected_icon=ft.Icons.RECEIPT_LONG, label="Facturas"),
            ]
        return []

    def on_nav_change(e):
        idx = e.control.selected_index
        role = app_state["role"]
        
        # Enrutamiento basado en Rol e Índice del Rail
        if role == "Administrador":
            views = ["dashboard", "usuarios", "productos", "inventario", "reportes", "clientes", "auditoria"]
            change_view(views[idx])
        elif role == "Supervisor":
            views = ["inventario", "productos", "auditoria"]
            change_view(views[idx])
        elif role == "Cajero":
            views = ["pos", "billing"]
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

    # --- Seguridad en Cierre de Caja (Imagen 8) ---
    tf_close_pass = ft.TextField(label="Contraseña", password=True, width=250)
    btn_confirm_close = ft.Button("Confirmar", bgcolor=DANGER_COLOR, color="white", disabled=True)

    def validate_close_pass(e):
        # El botón solo se habilita si la contraseña es válida (simulación)
        btn_confirm_close.disabled = len(tf_close_pass.value) < 4
        page.update()

    tf_close_pass.on_change = validate_close_pass

    def close_cash_session(e):
        # Finaliza turno y vuelve al login
        page.controls.clear()
        page.add(view_container)
        change_view("login")
        page.update()

    btn_confirm_close.on_click = close_cash_session

    def show_close_cash_modal(e):
        dialog = ft.AlertDialog(
            title=ft.Text("¿Está seguro de cerrar caja?", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Ingrese su contraseña para terminar el turno:", size=14, color=TEXT_SECONDARY),
                tf_close_pass
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                btn_confirm_close
            ],
            bgcolor=SURFACE_COLOR
        )
        page.overlay.append(dialog)
        dialog.open = True
        tf_close_pass.value = ""
        btn_confirm_close.disabled = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # Botón de cierre de caja (Acción crítica - Resaltado en rojo en menú lateral)
    close_cash_btn = ft.Container(
        content=ft.TextButton(
            "Cerrar caja",
            icon=ft.Icons.POWER_SETTINGS_NEW,
            style=ft.ButtonStyle(color=DANGER_COLOR),
            on_click=show_close_cash_modal
        ),
        padding=ft.Padding.only(bottom=20)
    )

    def change_view(name):
        # Limpieza y carga de vista
        view_container.content = None
        if name == "login":
            view_container.content = LoginView(page, on_login_success=login_success)
        elif name == "dashboard":
            view_container.content = DashboardView(page)
        elif name == "pos":
            view_container.content = POSView(page, lambda: change_view_from_internal("billing"))
        elif name == "billing":
            view_container.content = BillingView(page)
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
        # Navegación forzada desde dentro de una vista (ej: POS -> Facturación)
        if app_state["role"] == "Cajero":
            rail.selected_index = 1
        rail.update()
        change_view(name)

    def login_success(role):
        app_state["role"] = role
        rail.destinations = get_nav_destinations(role)
        rail.selected_index = 0
        rail.height=500
        rail.width=100
        page.controls.clear()
        
        # Layout principal con Side Panel + Área Central (Imagen 4)
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
        page.add(main_layout)
        
        # Vista inicial según rol
        if role == "Administrador": change_view("dashboard")
        elif role == "Supervisor": change_view("inventario")
        else: change_view("pos")

    # Inicio de la App
    page.add(view_container)
    change_view("login")

if __name__ == "__main__":
    ft.run(main)
