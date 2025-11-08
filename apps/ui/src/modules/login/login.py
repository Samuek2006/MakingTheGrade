import flet as ft
from ...API.crud import RestClient
from ...views.session import LoginUI
from ...views.dashboard import DashboardUI
from ..dashboard.dashboardLogic import DashboardLogic
from ..login.register import RegisterLogic

URL_API = "https://69069a11b1879c890ed7a77d.mockapi.io/"

class LoginLogic:
    def __init__(self, page: ft.Page, router=None):
        self.page = page
        self.router = router
        self._busy = False
        self.api = RestClient(base_url=URL_API)

        # Intentar leer el usuario recordado; si client_storage no está listo, seguir sin bloquear
        try:
            remembered_username = self.page.client_storage.get("remember_username") or ""
        except Exception as _:
            remembered_username = ""
        self.ui = LoginUI(page=self.page, controller=self, remembered_username=remembered_username)

    # === Helpers de UI ===
    def show_info(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    # === Navegación ===
    def ir_register(self, e=None):
        if self.router and hasattr(self.router, "show_register"):
            self.router.show_register()
        else:
            # Fallback directo si no usas router central
            self.page.clean()
            RegisterLogic(self.page)

    def continuar(self, user_obj: dict):
        # Usa el router si existe
        if self.router and hasattr(self.router, "show_dashboard"):
            self.router.show_dashboard(user_obj)
            return

        # Fallback: sin router, monta directo (con lógica para cargar pruebas)
        self.page.clean()
        self.page.add(DashboardUI(self.page, user=user_obj, logic=DashboardLogic(self.page, user=user_obj)))

    # === Verificación de credenciales ===
    def vefCredencialesUser(self, e, user_val: str | None = None, pwd_val: str | None = None):
        if self._busy:
            return

        # Soporte para ambas UIs: con self.ui.<control> o pasando valores por el botón
        user = (user_val if user_val is not None else (getattr(self.ui, "user", None).value if getattr(self.ui, "user", None) else "")).strip()
        pwd = (pwd_val if pwd_val is not None else (getattr(self.ui, "password", None).value if getattr(self.ui, "password", None) else ""))

        # Validaciones de UI
        if getattr(self.ui, "user", None) is not None:
            self.ui.user.error_text = None if user else "Ingresa tu usuario"
        if getattr(self.ui, "password", None) is not None:
            self.ui.password.error_text = None if pwd else "Ingresa tu contraseña"
        self.page.update()

        if not user or not pwd:
            return

        # Cargando…
        self._busy = True
        if getattr(self.ui, "login_btn", None) is not None:
            self.ui.login_btn.disabled = True
        self.page.update()

        try:
            # 1) Buscar por username
            ok_u, users, status_u, err_u = self.api.get("users", params={"search": user})
            if not ok_u:
                self.show_info(f"Error consultando usuarios (status {status_u}). {err_u or ''}")
                return

            # 2) Tomar el usuario exacto (username match)
            data = users or []
            usr = next((u for u in data if u.get("username") == user), None)
            if not usr:
                self.show_info("Usuario o contraseña inválidos")
                return

            # 3) Comparar contraseña (en tu registro usas 'password_hash' con la contraseña en claro)
            if str(usr.get("password_hash", "")) != str(pwd):
                self.show_info("Usuario o contraseña inválidos")
                return

            # 4) Recordarme
            if getattr(self.ui, "remember", None) is not None and self.ui.remember.value:
                self.page.client_storage.set("remember_username", user)
            else:
                self.page.client_storage.remove("remember_username")

            # 5) Éxito
            self.show_info("Inicio de sesión exitoso")
            self.continuar(usr)

        except Exception as ex:
            self.show_info(f"Error inesperado: {ex}")

        finally:
            self._busy = False
            if getattr(self.ui, "login_btn", None) is not None:
                self.ui.login_btn.disabled = False
            self.page.update()
