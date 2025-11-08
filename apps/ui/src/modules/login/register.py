# src/modules/login/register_logic.py
import flet as ft
from ...API.crud import RestClient
from ...views.session import RegisterUI

URL_API = "https://69069a11b1879c890ed7a77d.mockapi.io/"

class RegisterLogic:
    def __init__(self, page: ft.Page, router=None):
        self.page = page
        self.router = router         # <<--- guardar el router (AuthController)
        self.api = RestClient(base_url=URL_API)
        self._busy = False
        self.ui = RegisterUI(page=self.page, controller=self)

    # ======= Helpers UI =======
    def _toast(self, msg: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    # ======= Validación =======
    def validar(self) -> bool:
        ui = self.ui
        ok = True

        if not (ui.name_tf.value or "").strip():
            ui.name_tf.error_text = "Ingresa tu nombre"; ok = False
        else:
            ui.name_tf.error_text = None

        if not (ui.apellido_tf.value or "").strip():
            ui.apellido_tf.error_text = "Ingresa tu apellido"; ok = False
        else:
            ui.apellido_tf.error_text = None

        tel_val = (ui.tel_tf.value or "").strip()
        if not tel_val:
            ui.tel_tf.error_text = "Ingresa tu celular"; ok = False
        elif len(tel_val.replace("+", "")) < 7:
            ui.tel_tf.error_text = "Número de celular inválido"; ok = False
        else:
            ui.tel_tf.error_text = None

        user_val = (ui.user_tf.value or "").strip()
        if not user_val:
            ui.user_tf.error_text = "Ingresa tu usuario"; ok = False
        elif len(user_val) < 3:
            ui.user_tf.error_text = "El usuario debe tener al menos 3 caracteres"; ok = False
        else:
            ui.user_tf.error_text = None

        pwd_val = (ui.password_tf.value or "")
        if not pwd_val:
            ui.password_tf.error_text = "Ingresa tu contraseña"; ok = False
        elif len(pwd_val) < 6:
            ui.password_tf.error_text = "La contraseña debe tener al menos 6 caracteres"; ok = False
        else:
            ui.password_tf.error_text = None

        self.page.update()
        return ok

    # ======= Navegación =======
    def ir_login(self, e=None):
        if self.router and hasattr(self.router, "show_login"):
            self.router.show_login()
        else:
            # Fallback si no hay router:
            self.page.clean()
            # LoginLogic(self.page)
            self._toast("Vuelve al login desde el router.")

    # ======= Registro =======
    def registrar(self, e=None):
        if self._busy:
            return
        if not self.validar():
            return

        ui = self.ui
        username = ui.user_tf.value.strip()

        # 1) Verificar existencia
        ok_u, users, _, _ = self.api.get("users", params={"search": username})
        if ok_u and any((u or {}).get("username") == username for u in (users or [])):
            self._toast("El usuario ya existe")
            return

        # 2) Construir payload
        payload = {
            "nombre": (ui.name_tf.value or "").strip(),
            "apellido": (ui.apellido_tf.value or "").strip(),
            "telefono": (ui.tel_tf.value or "").strip(),
            "username": username,
            "password_hash": ui.password_tf.value,  # ojo: es solo demo, no hash real
            "rol": "user",
            "estado": "activo",
        }

        # 3) Deshabilitar botón y enviar
        self._busy = True
        try:
            ui.registrar_btn.disabled = True
            self.page.update()

            ok, data, status, err = self.api.post("users", json=payload)

            if ok:
                self._toast("Usuario registrado correctamente")
                self.ir_login(None)
            else:
                msg = f"Error al registrar usuario (status {status})"
                if err:
                    msg += f": {err}"
                self._toast(msg)
        finally:
            self._busy = False
            ui.registrar_btn.disabled = False
            self.page.update()
