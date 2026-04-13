import flet as ft
from core.colors import *

def InConstructionView(page: ft.Page, title: str):
    # Creamos un contenedor elegante que actúe como vista de reemplazo.
    # Explicación:
    # `ft.Container`: Componente usado como envoltorio para agregar fondos, alineación, padding.
    # `expand=True`: Le dice al contenedor que llene todo el espacio disponible.
    return ft.Container(
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.CONSTRUCTION, size=80, color=SECONDARY_COLOR),
                ft.Text(
                    value=f"Vista de {title}",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                ),
                ft.Text(
                    value="Esta sección se encuentra actualmente en desarrollo.",
                    size=16,
                    color=TEXT_SECONDARY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
