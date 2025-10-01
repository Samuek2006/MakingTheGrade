import flet as ft
from apps.ui.src.views.dashboard import Dashboard
from apps.ui.src.components.crud import create_user, authenticate_user
from uuid import uuid4
from passlib.hash import bcrypt
import json

# --- Botón reutilizable ---
class MyButton(ft.ElevatedButton):
    def __init__(self, text, on_click=None):
        super().__init__(
            text=text,
            bgcolor=ft.Colors.ORANGE_300,
            color=ft.Colors.GREEN_800,
            on_click=on_click,
        )

# --- REGISTER ---
class RegisterAPP:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Registro"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self._busy = False

        self.name_tf = ft.TextField(
            hint_text="Ingresa tu Nombre",
            width=360,
            autofocus=True,
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
            on_submit=lambda e: self.apellido_tf.focus(),
        )
        self.apellido_tf = ft.TextField(
            hint_text="Ingresa tu Apellido",
            width=360,
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
            on_submit=lambda e: self.tel_tf.focus(),
        )
        self.tel_tf = ft.TextField(
            hint_text="Ingresa tu Celular",
            width=360,
            prefix_icon=ft.Icons.PHONE_ANDROID,
            input_filter=ft.InputFilter(regex_string=r"[0-9+]", replacement_string=""),
            on_submit=lambda e: self.user_tf.focus(),
        )
        self.user_tf = ft.TextField(
            hint_text="Ingresa tu Usuario",
            width=360,
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
            on_submit=lambda e: self.password_tf.focus(),
        )
        self.password_tf = ft.TextField(
            hint_text="Ingresa tu Contraseña",
            width=360,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            on_submit=self.registrar,
        )

        self.registrar_btn = ft.FilledButton("Registrarme", on_click=self.registrar)
        self.registrar_btn.expand = True
        volver_login_btn = ft.OutlinedButton("Volver a Iniciar Sesión", on_click=self.ir_login)
        volver_login_btn.expand = True

        form = ft.Column(
            controls=[
                ft.Text("Crear cuenta", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.name_tf,
                self.apellido_tf,
                self.tel_tf,
                self.user_tf,
                self.password_tf,
                ft.Divider(),
                ft.Column(
                    [self.registrar_btn, volver_login_btn],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        card = ft.Card(
            content=ft.Container(width=420, padding=24, content=form),
            elevation=6,
        )
        self.page.add(ft.Container(expand=True, alignment=ft.alignment.center, content=card))

    def validar(self) -> bool:
        ok = True

        if not (self.name_tf.value or "").strip():
            self.name_tf.error_text = "Ingresa tu nombre"; ok = False
        else:
            self.name_tf.error_text = None

        if not (self.apellido_tf.value or "").strip():
            self.apellido_tf.error_text = "Ingresa tu apellido"; ok = False
        else:
            self.apellido_tf.error_text = None

        tel_val = (self.tel_tf.value or "").strip()
        if not tel_val:
            self.tel_tf.error_text = "Ingresa tu celular"; ok = False
        elif len(tel_val.replace("+", "")) < 7:
            self.tel_tf.error_text = "Número de celular inválido"; ok = False
        else:
            self.tel_tf.error_text = None

        user_val = (self.user_tf.value or "").strip()
        if not user_val:
            self.user_tf.error_text = "Ingresa tu usuario"; ok = False
        elif len(user_val) < 3:
            self.user_tf.error_text = "El usuario debe tener al menos 3 caracteres"; ok = False
        else:
            self.user_tf.error_text = None

        pwd_val = (self.password_tf.value or "")
        if not pwd_val:
            self.password_tf.error_text = "Ingresa tu contraseña"; ok = False
        elif len(pwd_val) < 6:
            self.password_tf.error_text = "La contraseña debe tener al menos 6 caracteres"; ok = False
        else:
            self.password_tf.error_text = None

        self.page.update()
        return ok

    def registrar(self, e):
        if self._busy:
            return
        if not self.validar():
            return

        self._busy = True
        self.registrar_btn.disabled = True
        self.page.update()

        try:
            identificacion = str(uuid4())
            password_hash = bcrypt.hash(self.password_tf.value)

            create_user(
                identificacion=identificacion,
                nombre=(self.name_tf.value or "").strip(),
                apellido=(self.apellido_tf.value or "").strip(),
                telefono=(self.tel_tf.value or "").strip(),
                username=(self.user_tf.value or "").strip(),
                password_hash=password_hash,
            )

            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Registro exitoso. Inicia sesión para continuar."))
            self.page.snack_bar.open = True
            self.page.update()

            self.ir_login(None)

        except ValueError as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
            self.page.snack_bar.open = True
            self.registrar_btn.disabled = False
            self._busy = False
            self.page.update()

        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error registrando: {ex}"))
            self.page.snack_bar.open = True
            self.registrar_btn.disabled = False
            self._busy = False
            self.page.update()

    def ir_login(self, e):
        self.page.clean()
        LoginAPP(self.page)

class LoginAPP:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Login"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self._busy = False

        remembered_username = self.page.client_storage.get("remember_username") or ""

        self.user = ft.TextField(
            hint_text="Ingresa tu Usuario",
            width=360,
            autofocus=True,
            value=remembered_username,
            prefix_icon=ft.Icons.PERSON_2_OUTLINED,
            on_submit=lambda e: self.password.focus(),
        )
        self.password = ft.TextField(
            hint_text="Ingresa tu Contraseña",
            width=360,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            on_submit=self.vefCredencialesUser,
        )

        self.remember = ft.Checkbox(label="Recordarme", value=bool(remembered_username))
        forgot_btn = ft.TextButton(
            "¿Olvidaste tu contraseña?",
            on_click=lambda e: self.show_info("Recuperación de contraseña no implementada aún."),
        )

        self.login_btn = MyButton("Ingresar", on_click=self.vefCredencialesUser)
        self.login_btn.expand = True
        register_btn = ft.OutlinedButton("Registrate Aquí", on_click=self.ir_register)
        register_btn.expand = True

        header = ft.Column(
            [ft.Text("Bienvenido", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Inicia sesión para continuar", size=14, color=ft.Colors.GREY_600)],
            spacing=4,
        )

        meta_row = ft.Row(
            [self.remember, ft.Container(expand=True), forgot_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        buttons_col = ft.Column(
            [self.login_btn, register_btn],
            spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        card_content = ft.Container(
            width=420, padding=ft.padding.all(24),
            content=ft.Column(
                controls=[header, ft.Divider(), self.user, self.password, meta_row, ft.Divider(), buttons_col],
                spacing=14, horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )
        card = ft.Card(content=card_content, elevation=6)
        self.page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                padding=ft.padding.symmetric(horizontal=16),
                content=card))

    def show_info(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def ir_register(self, e):
        self.page.clean()
        RegisterAPP(self.page)

    def vefCredencialesUser(self, e):
        if self._busy:
            return

        has_error = False
        if not (self.user.value or "").strip():
            self.user.error_text = "Ingresa tu usuario"; has_error = True
        else:
            self.user.error_text = None

        if not (self.password.value or ""):
            self.password.error_text = "Ingresa tu contraseña"; has_error = True
        else:
            self.password.error_text = None

        if has_error:
            self.page.update()
            return

        self._busy = True
        self.login_btn.disabled = True
        self.page.update()

        username = (self.user.value or "").strip()
        pwd = self.password.value

        try:
            print("[LOGIN] Autenticando:", username)
            user = authenticate_user(username, pwd)
            print("[LOGIN] Autenticado OK. id:", user.id)

            # Sesión
            if hasattr(self.page, "session"):
                self.page.session.set("current_user_id", str(user.id))
                self.page.session.set("current_user_name", user.nombre)
                self.page.session.set("current_user_role", getattr(user, "rol", None))

            # Recordarme
            if self.remember.value:
                self.page.client_storage.set("remember_username", username)
            else:
                self.page.client_storage.remove("remember_username")

            # Montar Dashboard
            print("[LOGIN] Limpiando página…")
            self.page.snack_bar = None
            self.page.clean()
            self.page.update()

            print("[LOGIN] Cargando Dashboard…")
            try:
                # import local evita circulares
                from .dashboard import Dashboard
                Dashboard(self.page)           # ← tu clase pinta directo en page
                self.page.update()
                print("[LOGIN] Dashboard cargado.")
            except Exception as dash_ex:
                print("[LOGIN] Error montando Dashboard:", dash_ex)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"No se pudo cargar el Dashboard: {dash_ex}"))
                self.page.snack_bar.open = True
                self.page.update()

        except ValueError as ex:
            self.password.error_text = None
            self.page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al iniciar sesión: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

        finally:
            self.login_btn.disabled = False
            self._busy = False
            self.page.update()
