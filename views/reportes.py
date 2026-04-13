import flet as ft
from core.colors import *

def ReportesView(page: ft.Page):
    """
    Módulo de Reportes (Imagen 14).
    Generación manual y automática de reportes.
    """
    
    # --- Panel Izquierdo (Generación) ---
    manual_panel = ft.Container(
        bgcolor=SURFACE_COLOR, padding=20, border_radius=10,
        content=ft.Column([
            ft.Text("Generar manualmente reportes", weight=ft.FontWeight.BOLD),
            ft.TextField(label="Fecha de inicio", hint_text="DD/MM/YYYY"),
            ft.TextField(label="Fecha de corte", hint_text="DD/MM/YYYY"),
            ft.Row([ft.OutlinedButton("Restablecer"), ft.ElevatedButton("Generar", bgcolor=PRIMARY_COLOR, color="white")], alignment=ft.MainAxisAlignment.END)
        ])
    )

    config_panel = ft.Container(
        bgcolor=SURFACE_COLOR, padding=20, border_radius=10,
        content=ft.Column([
            ft.Text("Generar automáticamente los reportes", weight=ft.FontWeight.BOLD),
            ft.TextField(label="Fecha de inicio"),
            ft.TextField(label="Fecha de corte"),
        ])
    )

    # --- Panel Derecho (Tabla de Resultados) ---
    search_bar = ft.TextField(hint_text="Buscar reporte...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    table = ft.DataTable(
        columns=[ft.DataColumn(label=ft.Text("Tipo de reporte")), ft.DataColumn(label=ft.Text("Fecha de creación")), ft.DataColumn(label=ft.Text("Acciones"))],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Ventas Mensuales")), ft.DataCell(ft.Text("01/04/2026")),
                ft.DataCell(ft.Row([ft.IconButton(ft.Icons.DELETE_OUTLINE), ft.IconButton(ft.Icons.PICTURE_AS_PDF, icon_color=DANGER_COLOR, tooltip="Descarga un PDF")]))
            ])
        ],
        expand=True
    )

    # --- Layout ---
    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([
            ft.Column([manual_panel, config_panel], expand=4, spacing=20),
            ft.VerticalDivider(width=1, color=DIVIDER_COLOR),
            ft.Column([
                ft.Text("Reportes", size=24, weight=ft.FontWeight.BOLD),
                search_bar,
                ft.Container(table, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
            ], expand=6)
        ], spacing=20)
    )
