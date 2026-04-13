import flet as ft
from core.colors import *
import datetime

def BillingView(page: ft.Page):
    """
    Módulo de Facturación (Imagen 7).
    Incluye búsqueda de clientes, adaptación según método de pago y registro rápido.
    """
    
    # --- Estado ---
    is_cash = ft.Ref[bool]()
    
    # --- Componentes Izquierda (Búsqueda de Clientes) ---
    search_client = ft.TextField(hint_text="Buscar cliente...", prefix_icon=ft.Icons.SEARCH, bgcolor=SURFACE_COLOR)
    client_table = ft.DataTable(
        columns=[ft.DataColumn(label=ft.Text("Nombre")), ft.DataColumn(label=ft.Text("Última compra"))],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Juan Pérez")), ft.DataCell(ft.Text("10/04/2026"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Maria Lopez")), ft.DataCell(ft.Text("05/04/2026"))]),
        ],
        expand=True
    )

    # --- Componentes Derecha (Formulario Adaptativo) ---
    tf_name = ft.TextField(label="Nombre y apellido", expand=True)
    tf_doc = ft.TextField(label="Cédula de ciudadanía", expand=True)
    
    # Campos de Tarjeta (Se omiten si es Efectivo - Imagen 7)
    card_fields = ft.Column([
        ft.TextField(label="Número de la tarjeta"),
        ft.Row([
            ft.TextField(label="Nombre del titular", expand=True),
            ft.TextField(label="Vencimiento (MM/YY)", width=150),
            ft.TextField(label="CVV", width=100, password=True),
        ]),
        ft.TextField(label="Cédula del titular")
    ], visible=True)

    def on_payment_change(e):
        # Lógica: Si es Efectivo, se omiten campos de tarjeta
        card_fields.visible = (e.control.value == "tarjeta")
        page.update()

    payment_method = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="tarjeta", label="Tarjeta de crédito/débito"),
            ft.Radio(value="efectivo", label="Efectivo"),
        ]),
        value="tarjeta",
        on_change=on_payment_change
    )

    # Totales y Métricas (Imagen 7)
    now = datetime.datetime.now()
    metrics_panel = ft.Container(
        bgcolor=SURFACE_COLOR, padding=15, border_radius=10,
        content=ft.Row([
            ft.Column([
                ft.Text(f"Subtotal: $ 15,000", size=12, color=TEXT_SECONDARY),
                ft.Text(f"Descuento: $ 0", size=12, color=TEXT_SECONDARY),
                ft.Text(f"IVA (19%): $ 2,850", size=12, color=TEXT_SECONDARY),
                ft.Text(f"Total: $ 17,850", weight=ft.FontWeight.BOLD, color=SECONDARY_COLOR),
            ]),
            ft.Column([
                ft.Text(f"Ítems: 3", size=12, color=TEXT_SECONDARY),
                ft.Text(f"Fecha: {now.strftime('%d/%m/%Y')}", size=12, color=TEXT_SECONDARY),
                ft.Text(f"Hora: {now.strftime('%H:%M %p')}", size=12, color=TEXT_SECONDARY),
            ]),
            ft.Column([
                ft.Text(f"Código de Fac:", size=12, color=TEXT_SECONDARY),
                ft.Text(f"FAC-000123", weight=ft.FontWeight.BOLD),
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    # --- Layout ---
    left_panel = ft.Column([
        ft.Text("Plantilla de Clientes", weight=ft.FontWeight.BOLD),
        search_client,
        ft.Container(client_table, bgcolor=SURFACE_COLOR, border_radius=10, padding=10, expand=True)
    ], expand=4)

    right_panel = ft.Column([
        ft.Text("Facturación", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([tf_name]),
        ft.Row([tf_doc]),
        ft.Divider(color=DIVIDER_COLOR),
        ft.Text("Método de pago", weight=ft.FontWeight.W_600),
        payment_method,
        card_fields,
        ft.Divider(color=DIVIDER_COLOR),
        ft.Row([
            ft.Text("Registrar nuevo cliente frecuente", size=14, color=TEXT_SECONDARY),
            ft.Switch(active_color=SECONDARY_COLOR)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        metrics_panel,
        ft.Row([
            ft.OutlinedButton("Restablecer", expand=True),
            ft.ElevatedButton("Facturar", bgcolor=SUCCESS_COLOR, color="white", expand=True)
        ], spacing=10)
    ], expand=6, scroll=ft.ScrollMode.AUTO)

    return ft.Container(
        expand=True, padding=20, bgcolor=BACKGROUND_COLOR,
        content=ft.Row([left_panel, ft.VerticalDivider(width=1, color=DIVIDER_COLOR), right_panel], spacing=20)
    )
