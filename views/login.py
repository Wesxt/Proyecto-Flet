import flet as ft
from core.colors import *
from controllers.login_controller import LoginController

class LoginView(ft.Container):
    def __init__(self, page: ft.Page, on_login_success):
        super().__init__(
            expand=True,
            bgcolor=BACKGROUND_COLOR,
            alignment=ft.Alignment.CENTER
        )
        self.page_ref = page
        self.controller = LoginController(self, on_login_success)
        
        self.build_ui()

    def build_ui(self):
        # --- Componentes de Inicio de Sesión (Imagen 1) ---
        self.tf_user = ft.TextField(
            label="Nombre de usuario",
            border_color=PRIMARY_COLOR,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            color=TEXT_PRIMARY,
            focused_border_color=SECONDARY_COLOR
        )
        
        self.tf_pass = ft.TextField(
            label="Contraseña",
            border_color=PRIMARY_COLOR,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            color=TEXT_PRIMARY,
            focused_border_color=SECONDARY_COLOR
        )

        # --- Componentes de Recuperación (Imagen 2) ---
        self.tf_recovery_email = ft.TextField(label="E-mail", border_color=PRIMARY_COLOR)
        self.tf_new_pass = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True, border_color=PRIMARY_COLOR)
        self.tf_confirm_pass = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, border_color=PRIMARY_COLOR)
        
        self.recovery_info_text = ft.Text(
            "Se ha enviado una verificación al correo ingresado. Una vez verificado, podrás acceder.",
            color=SECONDARY_COLOR,
            size=12,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )

        self.error_text = ft.Text(
            "",
            color=DANGER_COLOR,
            size=14,
            weight=ft.FontWeight.W_500,
            visible=False
        )

        def clear_error(e):
            self.error_text.visible = False
            self.page_ref.update()

        self.tf_user.on_change = clear_error
        self.tf_pass.on_change = clear_error

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
                    self.tf_user,
                    self.tf_pass,
                    self.error_text,
                    ft.TextButton(
                        "¿Se le olvidó la contraseña?",
                        style=ft.ButtonStyle(color=TEXT_SECONDARY),
                        on_click=self.open_recovery_modal
                    ),
                    ft.Button(
                        "Iniciar sesión",
                        bgcolor=PRIMARY_COLOR,
                        color="white",
                        width=300,
                        height=50,
                        on_click=lambda e: self.controller.do_login(self.tf_user.value, self.tf_pass.value)
                    )
                ]
            )
        )
        self.content = login_card

    def show_error(self, message):
            self.error_text.value = message
            self.error_text.visible = True
            self.page_ref.update()

    def show_recovery_info(self):
        self.recovery_info_text.visible = True
        self.page_ref.update()

    def open_recovery_modal(self, e):
        dialog = ft.AlertDialog(
            title=ft.Text("Recuperación de Contraseña", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Ingresa tu correo registrado para restablecer tu cuenta.", size=14, color=TEXT_SECONDARY),
                self.tf_recovery_email,
                self.tf_new_pass,
                self.tf_confirm_pass,
                self.recovery_info_text
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dialog)),
                ft.Button(
                    "Enviar verificación", 
                    bgcolor=PRIMARY_COLOR, 
                    color="white", 
                    on_click=lambda _: self.controller.send_recovery_verification(
                        self.tf_recovery_email.value, 
                        self.tf_new_pass.value, 
                        self.tf_confirm_pass.value
                    )
                )
            ],
            bgcolor=SURFACE_COLOR,
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
        )
        self.page_ref.show_dialog(dialog)
        self.page_ref.update()

    def close_dialog(self, dialog):
        self.page_ref.pop_dialog()
        self.recovery_info_text.visible = False
        self.page_ref.update()
