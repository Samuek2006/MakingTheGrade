import flet as ft
from ...API.crud import RestClient
from ...views.session import LoginUI
from ...views.dashboard import DashboardUI
from ...views.loading_overlay import LoadingOverlay
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
        
        # Crear overlay de carga (inicialmente oculto)
        self.loading_overlay = LoadingOverlay(page=self.page, message="Verificando credenciales...")
        self.loading_overlay.visible = False

    # === Helpers de UI ===
    def show_info(self, msg: str, is_error: bool = False):
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        bg_color = getattr(C, "RED_600", getattr(C, "RED", None)) if is_error else None
        
        try:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(msg, color=getattr(C, "WHITE", "#FFFFFF") if is_error else None),
                bgcolor=bg_color,
                duration=5000 if is_error else 3000,
                action="OK" if is_error else None,
                action_color=getattr(C, "WHITE", "#FFFFFF") if is_error else None,
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            # Fallback simple
            print(f"Error en show_info: {ex}")
            try:
                self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=bg_color)
                self.page.snack_bar.open = True
                self.page.update()
            except:
                pass
    
    def show_loading(self, message: str = "Verificando credenciales..."):
        """Muestra el overlay de carga"""
        # Primero agregar al overlay si no está (esto lo agrega a la página)
        if self.loading_overlay not in self.page.overlay:
            self.page.overlay.append(self.loading_overlay)
            self.page.update()  # Actualizar para que se agregue a la página
        
        # Ahora sí podemos actualizar el mensaje y mostrarlo
        self.loading_overlay.visible = True
        self.loading_overlay.loading_text.value = message
        self.loading_overlay.message = message
        self.loading_overlay.show()
        self.page.update()
    
    def hide_loading(self):
        """Oculta el overlay de carga"""
        self.loading_overlay.hide()
        self.page.update()
        
        # Remover del overlay después de la animación usando un timer de Flet
        def remove_overlay(e=None):
            try:
                if self.loading_overlay in self.page.overlay:
                    self.page.overlay.remove(self.loading_overlay)
                self.loading_overlay.visible = False
                self.page.update()
            except:
                pass
        
        # Usar un timer de Flet para remover después de 300ms (duración de la animación)
        try:
            timer = ft.Timer(interval=300, once=True, on_tick=remove_overlay)
            self.page.overlay.append(timer)
        except:
            remove_overlay()
    
    def _show_error_after_loading(self, message: str):
        """Muestra un error después de ocultar el overlay"""
        def show_error(e=None):
            try:
                C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
                bg_color = getattr(C, "RED_600", getattr(C, "RED", None))
                
                # Asegurarse de que el snackbar se muestre correctamente
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(message, color=getattr(C, "WHITE", "#FFFFFF")),
                    bgcolor=bg_color,
                    duration=5000,  # 5 segundos para errores
                    action="OK",
                    action_color=getattr(C, "WHITE", "#FFFFFF"),
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as ex:
                # Fallback simple
                print(f"Error mostrando snackbar: {ex}")
        
        # Esperar un poco para que el overlay se oculte completamente
        try:
            error_timer = ft.Timer(interval=400, once=True, on_tick=show_error)
            self.page.overlay.append(error_timer)
        except:
            # Si el timer falla, mostrar directamente después de un pequeño delay
            import time
            import threading
            def delayed_show():
                time.sleep(0.4)
                self.page.run_task(show_error)
            threading.Thread(target=delayed_show, daemon=True).start()

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
        
        # Mostrar overlay de carga
        self.show_loading("Verificando credenciales...")
        self.page.update()

        try:
            # 1) Buscar por username
            self.loading_overlay.loading_text.value = "Buscando usuario..."
            self.loading_overlay.message = "Buscando usuario..."
            self.page.update()
            
            ok_u, users, status_u, err_u = self.api.get("users", params={"search": user})
            if not ok_u:
                # Ocultar overlay primero
                self.loading_overlay.opacity = 0.0
                self.loading_overlay.visible = False
                if self.loading_overlay in self.page.overlay:
                    self.page.overlay.remove(self.loading_overlay)
                self.page.update()
                # Mostrar error inmediatamente
                self.show_info(f"Error consultando usuarios (status {status_u}). {err_u or ''}", is_error=True)
                return

            # 2) Tomar el usuario exacto (username match)
            data = users or []
            usr = next((u for u in data if u.get("username") == user), None)
            if not usr:
                # Ocultar overlay primero
                self.loading_overlay.opacity = 0.0
                self.loading_overlay.visible = False
                if self.loading_overlay in self.page.overlay:
                    self.page.overlay.remove(self.loading_overlay)
                # Resaltar el campo de usuario con error
                if getattr(self.ui, "user", None) is not None:
                    self.ui.user.error_text = "Usuario no encontrado"
                    self.ui.user.focus()
                self.page.update()
                # Mostrar error inmediatamente
                self.show_info("El usuario ingresado no existe. Por favor, verifica tu usuario.", is_error=True)
                return

            # 3) Comparar contraseña (en tu registro usas 'password_hash' con la contraseña en claro)
            self.loading_overlay.loading_text.value = "Verificando contraseña..."
            self.loading_overlay.message = "Verificando contraseña..."
            self.page.update()
            
            if str(usr.get("password_hash", "")) != str(pwd):
                # Ocultar overlay primero
                self.loading_overlay.opacity = 0.0
                self.loading_overlay.visible = False
                if self.loading_overlay in self.page.overlay:
                    self.page.overlay.remove(self.loading_overlay)
                # Resaltar el campo de contraseña con error
                if getattr(self.ui, "password", None) is not None:
                    self.ui.password.error_text = "Contraseña incorrecta"
                    self.ui.password.focus()
                self.page.update()
                # Mostrar error inmediatamente
                self.show_info("La contraseña ingresada es incorrecta. Por favor, intenta nuevamente.", is_error=True)
                return

            # 4) Recordarme
            if getattr(self.ui, "remember", None) is not None and self.ui.remember.value:
                self.page.client_storage.set("remember_username", user)
            else:
                self.page.client_storage.remove("remember_username")

            # 5) Éxito
            self.loading_overlay.loading_text.value = "¡Inicio de sesión exitoso!"
            self.loading_overlay.message = "¡Inicio de sesión exitoso!"
            self.page.update()
            
            # Pequeño delay antes de continuar para mostrar el mensaje de éxito
            def continue_after_delay(e=None):
                self.hide_loading()
                self.show_info("Inicio de sesión exitoso")
                self.continuar(usr)
            
            # Usar timer de Flet para el delay
            try:
                success_timer = ft.Timer(interval=500, once=True, on_tick=continue_after_delay)
                self.page.overlay.append(success_timer)
            except:
                # Fallback si el timer no funciona
                continue_after_delay()
                return

        except Exception as ex:
            # Ocultar overlay primero
            self.loading_overlay.opacity = 0.0
            self.loading_overlay.visible = False
            if self.loading_overlay in self.page.overlay:
                self.page.overlay.remove(self.loading_overlay)
            self.page.update()
            # Mostrar error inmediatamente
            self.show_info(f"Error inesperado: {ex}", is_error=True)

        finally:
            self._busy = False
            if getattr(self.ui, "login_btn", None) is not None:
                self.ui.login_btn.disabled = False
            self.page.update()
