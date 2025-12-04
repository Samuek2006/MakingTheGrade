import flet as ft
from ..utils.buttonLogin import ButtonLogin

# ======================================
#            REGISTER  (UI)
# ======================================
class RegisterUI(ft.Column):
    def __init__(self, page: ft.Page, controller):
        super().__init__(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.page = page
        self.controller = controller

        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        PRIMARY = getattr(C, "BLUE_700", getattr(C, "BLUE", None))
        TEXT_MUTED = getattr(C, "GREY_600", None)

        # ---------- Config opcional de página ----------
        self.page.title = "Registro"
        self.page.padding = 0
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.bgcolor = getattr(C, "GREY_50", None)
        try:
            self.page.theme = ft.Theme(color_scheme_seed=getattr(C, "BLUE", None), use_material3=True)
        except Exception:
            pass

        def field(**kw):
            return ft.TextField(
                expand=True,  # Se adapta al ancho disponible
                border_radius=12,
                border_color=getattr(C, "GREY_400", None),
                focused_border_color=PRIMARY,
                cursor_color=PRIMARY,
                hint_style=ft.TextStyle(size=15, color=TEXT_MUTED),
                text_style=ft.TextStyle(size=16),
                content_padding=ft.padding.symmetric(14, 16),
                **kw,
            )

        # ---------- Campos ----------
        self.name_tf = field(
            hint_text="Ingresa tu Nombre",
            autofocus=True,
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
        )
        self.apellido_tf = field(
            hint_text="Ingresa tu Apellido",
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
        )
        self.tel_tf = field(
            hint_text="Ingresa tu Celular",
            prefix_icon=ft.Icons.PHONE_ANDROID,
            input_filter=ft.InputFilter(regex_string=r"[0-9+]", replacement_string=""),
        )
        self.user_tf = field(
            hint_text="Ingresa tu Usuario",
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
        )
        self.password_tf = field(
            hint_text="Ingresa tu Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )

        # ---------- Botones ----------
        self.registrar_btn = ft.FilledButton(
            "Registrarme",
            icon=ft.Icons.HOW_TO_REG,
            on_click=self.controller.registrar,   # <-- Llama a la lógica de registro
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY},
                color=getattr(C, "WHITE", None),
                padding=ft.padding.symmetric(14, 0),
                shape=ft.RoundedRectangleBorder(radius=26),
                elevation=6,
            ),
        )
        self.volver_login_btn = ft.OutlinedButton(
            "Volver a Iniciar Sesión",
            icon=ft.Icons.LOGIN,
            on_click=self.controller.ir_login,
            style=ft.ButtonStyle(
                side={ft.ControlState.DEFAULT: ft.BorderSide(1.2, PRIMARY)},
                color=PRIMARY,
                padding=ft.padding.symmetric(12, 0),
                shape=ft.RoundedRectangleBorder(radius=26),
            ),
        )

        # ---------- Estructura ----------
        header = ft.Column(
            [
                ft.Text("Crear cuenta", size=28, weight=ft.FontWeight.W_700),
                ft.Text("Únete y empieza a usar la app en segundos.", size=14, color=TEXT_MUTED),
            ],
            spacing=6,
        )

        form = ft.Column(
            controls=[
                header,
                ft.Divider(),
                self.name_tf,
                self.apellido_tf,
                self.tel_tf,
                self.user_tf,
                self.password_tf,
                ft.Container(height=6),
                ft.Divider(),
                ft.Column(
                    [self.registrar_btn, self.volver_login_btn],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        card = ft.Card(
            elevation=8,
            surface_tint_color=getattr(C, "WHITE", None),
            content=ft.Container(
                padding=ft.padding.symmetric(horizontal=24, vertical=24),
                content=form,
            ),
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Container(
                    content=card,
                    width=520,  # Ancho fijo para pantallas grandes
                    padding=ft.padding.symmetric(horizontal=16, vertical=20),
                ),
                padding=ft.padding.symmetric(horizontal=16),  # Padding adicional para móviles
            )
        ]

class LoginUI(ft.Column):
    def __init__(self, page: ft.Page, controller, remembered_username: str = ""):
        super().__init__(spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.page = page
        self.controller = controller

        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        PRIMARY = getattr(C, "BLUE_700", getattr(C, "BLUE", None))
        PRIMARY_LIGHT = getattr(C, "BLUE_600", getattr(C, "BLUE", None))
        ACCENT = getattr(C, "AMBER_400", None)
        ACCENT_LIGHT = getattr(C, "AMBER_300", None)
        TEXT_MUTED = getattr(C, "GREY_600", None)
        TEXT_SECONDARY = getattr(C, "GREY_700", None)
        BORDER = getattr(C, "GREY_300", None)
        BORDER_FOCUS = getattr(C, "BLUE_500", None)
        BG_PAGE = getattr(C, "GREY_50", None)
        BG_CARD = getattr(C, "WHITE", None)
        ERROR = getattr(C, "RED_600", getattr(C, "RED", None))
        SUCCESS = getattr(C, "GREEN_600", getattr(C, "GREEN", None))

        self.page.title = "Login"
        self.page.padding = 0
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.bgcolor = BG_PAGE

        # ----- helpers de UI mejorados con responsive -----
        def field(**kw):
            return ft.TextField(
                expand=True,  # Se adapta al ancho disponible
                border_radius=16,
                border_color=BORDER,
                focused_border_color=PRIMARY,
                border_width=1.5,
                focused_border_width=2,
                cursor_color=PRIMARY,
                cursor_width=2,
                hint_style=ft.TextStyle(size=15, color=TEXT_MUTED, weight=ft.FontWeight.W_400),
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500),
                content_padding=ft.padding.symmetric(18, 20),
                bgcolor=BG_CARD,
                filled=True,
                **kw,
            )

        def submit_if_valid(e=None):
            if self._validate_all():
                self.controller.vefCredencialesUser(e, self.user.value.strip(), self.password.value)

        # ----- Campos mejorados -----
        self.user = field(
            hint_text="Ingresa tu Usuario",
            autofocus=True,
            value=remembered_username,
            prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
        )
        self.password = field(
            hint_text="Ingresa tu Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
        )

        # Validaciones en tiempo real
        self.user.on_change = lambda e: self._clear_error_if_valid("user")
        self.user.on_blur = lambda e: self._validate_user()
        self.password.on_change = lambda e: self._clear_error_if_valid("password")
        self.password.on_blur = lambda e: self._validate_password()

        # Submit con Enter
        self.user.on_submit = lambda e: self.password.focus()
        self.password.on_submit = submit_if_valid

        # Checkbox mejorado
        self.remember = ft.Checkbox(
            label="Recordarme",
            value=bool(remembered_username),
            fill_color=PRIMARY,
            check_color=getattr(C, "WHITE", None),
            label_style=ft.TextStyle(size=14, color=TEXT_SECONDARY),
        )

        # Botón de olvidar contraseña mejorado
        forgot_btn = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=lambda e: self._info("Recuperación de contraseña no implementada aún."),
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: PRIMARY},
                overlay_color={ft.ControlState.HOVERED: ft.colors.with_opacity(0.1, PRIMARY) if hasattr(ft, "colors") else None},
            ),
        )

        # ----- Botones mejorados -----
        try:
            from ..utils.buttonLogin import ButtonLogin
            self.login_btn = ButtonLogin("Ingresar", on_click=submit_if_valid)
        except Exception:
            self.login_btn = ft.FilledButton(
                "Ingresar",
                icon=ft.Icons.LOGIN_ROUNDED,
                on_click=submit_if_valid,
                style=ft.ButtonStyle(
                    bgcolor={ft.ControlState.DEFAULT: PRIMARY},
                    color={ft.ControlState.DEFAULT: getattr(C, "WHITE", None)},
                    overlay_color={ft.ControlState.HOVERED: PRIMARY_LIGHT},
                    padding=ft.padding.symmetric(18, 0),
                    shape=ft.RoundedRectangleBorder(radius=16),
                    elevation={ft.ControlState.DEFAULT: 4, ft.ControlState.HOVERED: 8},
                    animation_duration=200,
                ),
            )
        self.login_btn.expand = True

        self.register_btn = ft.OutlinedButton(
            "Crear cuenta nueva",
            icon=ft.Icons.PERSON_ADD_ROUNDED,
            on_click=self.controller.ir_register,
            style=ft.ButtonStyle(
                side={ft.ControlState.DEFAULT: ft.BorderSide(1.5, PRIMARY)},
                color={ft.ControlState.DEFAULT: PRIMARY},
                overlay_color={ft.ControlState.HOVERED: ft.colors.with_opacity(0.1, PRIMARY) if hasattr(ft, "colors") else None},
                shape=ft.RoundedRectangleBorder(radius=16),
                padding=ft.padding.symmetric(16, 0),
                animation_duration=200,
            ),
        )
        self.register_btn.expand = True

        # Header mejorado con gradiente sutil
        title = ft.Text(
            "Bienvenido de nuevo",
            size=32,
            weight=ft.FontWeight.W_700,
            color=TEXT_SECONDARY,
        )
        subtitle = ft.Text(
            "Inicia sesión para acceder a tu cuenta",
            size=15,
            color=TEXT_MUTED,
            weight=ft.FontWeight.W_400,
        )

        # Badge de seguridad mejorado
        header_badge = ft.Container(
            bgcolor=ft.colors.with_opacity(0.12, ACCENT) if hasattr(ft, "colors") else None,
            padding=ft.padding.symmetric(12, 16),
            border_radius=12,
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ACCENT) if hasattr(ft, "colors") else None),
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.VERIFIED_USER_ROUNDED,
                        size=22,
                        color=ACCENT,
                    ),
                    ft.Text(
                        "Conexión segura y encriptada",
                        size=13,
                        color=TEXT_SECONDARY,
                        weight=ft.FontWeight.W_500,
                    )
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

        header = ft.Column(
            [
                ft.Container(
                    content=ft.Column([title, subtitle], spacing=4),
                    padding=ft.padding.only(bottom=8),
                ),
                header_badge,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

        # Meta row mejorado
        meta_row = ft.Row(
            [self.remember, ft.Container(expand=True), forgot_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Botones con mejor espaciado
        buttons_col = ft.Column(
            [self.login_btn, self.register_btn],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # Card body mejorado
        card_body = ft.Column(
            controls=[
                header,
                ft.Container(height=24),
                self.user,
                ft.Container(height=4),
                self.password,
                ft.Container(height=8),
                meta_row,
                ft.Container(height=20),
                buttons_col,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # Card con sombra mejorada y responsive
        card = ft.Card(
            elevation=12,
            shadow_color=ft.colors.with_opacity(0.15, getattr(C, "BLACK", None)) if hasattr(ft, "colors") else None,
            surface_tint_color=BG_CARD,
            content=ft.Container(
                padding=ft.padding.symmetric(
                    horizontal=24,  # Padding horizontal responsive
                    vertical=32
                ),
                content=card_body,
            ),
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Container(
                    content=card,
                    width=520,  # Ancho fijo para pantallas grandes
                    padding=ft.padding.symmetric(
                        horizontal=16,  # Padding responsive
                        vertical=20
                    ),
                ),
                padding=ft.padding.symmetric(horizontal=16),  # Padding adicional para móviles
            )
        ]

        # ==== MÉTODOS DE VALIDACIÓN (UI) ====
        self._ERROR_COLOR = ERROR

    # --------- VALIDADORES ----------
    def _validate_user(self) -> bool:
        val = (self.user.value or "").strip()
        if not val:
            self.user.error_text = "Ingresa tu usuario"
        elif len(val) < 3:
            self.user.error_text = "El usuario debe tener al menos 3 caracteres"
        else:
            self.user.error_text = None
        self.page.update()
        if self.user.error_text:
            self._alert(self.user.error_text)
            return False
        return True

    def _validate_password(self) -> bool:
        val = self.password.value or ""
        if not val:
            self.password.error_text = "Ingresa tu contraseña"
        elif len(val) < 6:
            self.password.error_text = "La contraseña debe tener al menos 6 caracteres"
        else:
            self.password.error_text = None
        self.page.update()
        if self.password.error_text:
            self._alert(self.password.error_text)
            return False
        return True

    def _validate_all(self) -> bool:
        ok_user = self._validate_user()
        ok_pwd = self._validate_password()
        return ok_user and ok_pwd

    def _clear_error_if_valid(self, which: str):
        if which == "user":
            val = (self.user.value or "").strip()
            if val and len(val) >= 3 and self.user.error_text:
                self.user.error_text = None
                self.page.update()
        elif which == "password":
            val = self.password.value or ""
            if val and len(val) >= 6 and self.password.error_text:
                self.password.error_text = None
                self.page.update()

    # --------- ALERTAS ----------
    def _alert(self, msg: str):
        self.page.snack_bar = ft.SnackBar(
            ft.Text(msg),
            bgcolor=self._ERROR_COLOR,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _info(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()
