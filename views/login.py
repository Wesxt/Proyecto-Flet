import flet as ft
from core.colors import *
from core.database import get_connection

def LoginView(page: ft.Page, on_login_success):
    """
    Vista de Inicio de Sesión y Recuperación de Contraseña.
    Basada en las Imágenes 1 y 2 de la documentación.
    """
    
    # --- Componentes de Inicio de Sesión (Imagen 1) ---
    tf_user = ft.TextField(
        label="Nombre de usuario",
        border_color=PRIMARY_COLOR,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        color=TEXT_PRIMARY,
        focused_border_color=SECONDARY_COLOR
    )
    
    tf_pass = ft.TextField(
        label="Contraseña",
        border_color=PRIMARY_COLOR,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        color=TEXT_PRIMARY,
        focused_border_color=SECONDARY_COLOR
    )

    # --- Componentes de Recuperación (Imagen 2) ---
    tf_recovery_email = ft.TextField(label="E-mail", border_color=PRIMARY_COLOR)
    tf_new_pass = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, border_color=PRIMARY_COLOR)
    tf_confirm_pass = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, border_color=PRIMARY_COLOR)
    
    recovery_info_text = ft.Text(
        "Se ha enviado una verificación al correo ingresado. Una vez verificado, podrás acceder.",
        color=SECONDARY_COLOR,
        size=12,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
        visible=False
    )

    def do_login(e):
        username = tf_user.value
        password = tf_pass.value
        
        if not username or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingrese usuario y contraseña"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ? AND status = 1", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            role = user["role"]
            on_login_success(role, username)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuario o contraseña incorrectos"), bgcolor=DANGER_COLOR)
            page.snack_bar.open = True
            page.update()

    def open_recovery_modal(e):
        # El documento especifica que la recuperación es un flujo alterno (Imagen 2)
        # Usamos un modal para capturar los datos de recuperación
        dialog = ft.AlertDialog(
            title=ft.Text("Recuperación de Contraseña", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Ingresa tu correo registrado para restablecer tu cuenta.", size=14, color=TEXT_SECONDARY),
                tf_recovery_email,
                tf_new_pass,
                tf_confirm_pass,
                recovery_info_text
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog(dialog)),
                ft.Button("Enviar verificación", bgcolor=PRIMARY_COLOR, color="white", on_click=lambda _: send_verification(dialog))
            ],
            bgcolor=SURFACE_COLOR,
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def send_verification(dialog):
        # Muestra el texto informativo rosa especificado en el doc
        recovery_info_text.visible = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        recovery_info_text.visible = False
        page.update()

    # Layout de la Tarjeta de Login
    login_card = ft.Container(
        width=380,
        padding=40,
        bgcolor=SURFACE_COLOR,
        border_radius=BORDER_RADIUS,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color="#66000000"),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.LOCK_PERSON_ROUNDED, size=50, color=PRIMARY_COLOR),
                ft.Text("Bienvenido", size=28, weight=ft.FontWeight.BOLD),
                tf_user,
                tf_pass,
                ft.TextButton(
                    "¿Se le olvidó la contraseña?",
                    style=ft.ButtonStyle(color=TEXT_SECONDARY),
                    on_click=open_recovery_modal
                ),
                ft.Button(
                    "Iniciar sesión",
                    bgcolor=PRIMARY_COLOR,
                    color="white",
                    width=300,
                    height=50,
                    on_click=do_login
                )
            ]
        )
    )

    return ft.Container(
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        alignment=ft.Alignment.CENTER,
        content=login_card
    )
