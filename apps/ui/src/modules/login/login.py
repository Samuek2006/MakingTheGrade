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
        """Muestra un mensaje en snackbar - formato simple que funciona"""
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        
        # Formato simple como en otras partes del código
        if is_error:
            # Para errores: fondo rojo, texto blanco
            self.page.snack_bar = ft.SnackBar(
                ft.Text(msg, color=getattr(C, "WHITE", "#FFFFFF")),
                bgcolor=getattr(C, "RED_600", getattr(C, "RED", None)),
                duration=5000,
            )
        else:
            # Para info normal
            self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        
        self.page.snack_bar.open = True
        self.page.update()
    
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
    
    def _remove_overlay(self):
        """Remueve el overlay completamente de forma inmediata"""
        try:
            # Cerrar el overlay
            self.loading_overlay.opacity = 0.0
            self.loading_overlay.visible = False
            # Remover del overlay de la página
            if hasattr(self.page, 'overlay') and self.loading_overlay in self.page.overlay:
                self.page.overlay.remove(self.loading_overlay)
            # Forzar update
            self.page.update()
        except Exception as e:
            print(f"Error removiendo overlay: {e}")
    
    def hide_loading(self):
        """Oculta el overlay de carga"""
        self._remove_overlay()

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
        self.page.views.clear()  # Limpiar vistas en lugar de clean()
        dash_logic = DashboardLogic(self.page, user=user_obj)
        dash_ui = DashboardUI(self.page, user=user_obj, logic=dash_logic, controller=self.router)
        view = ft.View(route="/dashboard", controls=[dash_ui])
        self.page.views.append(view)
        self.page.update()

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

        # 1) Buscar por username
        self.loading_overlay.loading_text.value = "Buscando usuario..."
        self.loading_overlay.message = "Buscando usuario..."
        self.page.update()
        
        # Pequeño delay para que se vea la animación de "Buscando usuario..."
        import threading
        import time
        
        # Usar threading para no bloquear, pero esperar un poco
        def delayed_search():
            time.sleep(0.8)  # Esperar 0.8 segundos para que se vea la animación
            try:
                ok_u, users, status_u, err_u = self.api.get("users", params={"search": user})
                # Procesar resultado en el hilo principal usando async wrapper
                async def process_search():
                    self._process_user_search(ok_u, users, status_u, err_u, user, pwd)
                self.page.run_task(process_search)
            except Exception as ex:
                # Manejar error usando async wrapper
                async def handle_error():
                    self._handle_search_error(ex)
                self.page.run_task(handle_error)
        
        threading.Thread(target=delayed_search, daemon=True).start()
    
    def _handle_search_error(self, ex):
        """Maneja errores en la búsqueda de usuario"""
        self._remove_overlay()
        self._busy = False
        if getattr(self.ui, "login_btn", None) is not None:
            self.ui.login_btn.disabled = False
        self.page.update()
        C = getattr(ft, "Colors", None) or getattr(ft, "colors", None)
        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"Error inesperado: {ex}", color=getattr(C, "WHITE", "#FFFFFF")),
            bgcolor=getattr(C, "RED_600", getattr(C, "RED", None)),
            duration=5000,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _process_user_search(self, ok_u, users, status_u, err_u, user, pwd):
        """Procesa el resultado de la búsqueda de usuario"""
        try:
            if not ok_u:
                # Ocultar overlay completamente
                self._remove_overlay()
                # Resetear estado de busy
                self._busy = False
                if getattr(self.ui, "login_btn", None) is not None:
                    self.ui.login_btn.disabled = False
                # Mostrar error
                self.show_info(f"Error consultando usuarios (status {status_u}). {err_u or ''}", is_error=True)
                return

            # 2) Tomar el usuario exacto (username match)
            data = users or []
            usr = next((u for u in data if u.get("username") == user), None)
            if not usr:
                # Asegurarse de que el overlay esté visible y mostrar error
                if self.loading_overlay not in self.page.overlay:
                    self.page.overlay.append(self.loading_overlay)
                self.loading_overlay.visible = True
                self.loading_overlay.opacity = 1.0
                self.page.update()
                
                # Mostrar error en la animación (X roja con mensaje)
                # Duración suficiente para que se vea bien
                duration = 2000  # 2 segundos
                self.loading_overlay.show_error(duration=duration)
                
                # Resetear estado de busy después del error
                def reset_busy():
                    self._busy = False
                    if getattr(self.ui, "login_btn", None) is not None:
                        self.ui.login_btn.disabled = False
                    self.page.update()
                
                # Resetear después de que se oculte el error
                try:
                    reset_timer = ft.Timer(interval=duration + 100, once=True, on_tick=lambda e: reset_busy())
                    self.page.overlay.append(reset_timer)
                except:
                    import threading
                    import time
                    threading.Thread(target=lambda: (time.sleep((duration + 100) / 1000.0), reset_busy()), daemon=True).start()
                return

            # 3) Comparar contraseña (en tu registro usas 'password_hash' con la contraseña en claro)
            self.loading_overlay.loading_text.value = "Verificando contraseña..."
            self.loading_overlay.message = "Verificando contraseña..."
            self.page.update()
            
            if str(usr.get("password_hash", "")) != str(pwd):
                # Asegurarse de que el overlay esté visible y mostrar error
                if self.loading_overlay not in self.page.overlay:
                    self.page.overlay.append(self.loading_overlay)
                self.loading_overlay.visible = True
                self.loading_overlay.opacity = 1.0
                self.page.update()
                
                # Mostrar error en la animación (X roja con mensaje)
                # Duración suficiente para que se vea bien
                duration = 2000  # 2 segundos
                self.loading_overlay.show_error(duration=duration)
                
                # Resetear estado de busy después del error
                def reset_busy():
                    self._busy = False
                    if getattr(self.ui, "login_btn", None) is not None:
                        self.ui.login_btn.disabled = False
                    self.page.update()
                
                # Resetear después de que se oculte el error
                try:
                    reset_timer = ft.Timer(interval=duration + 100, once=True, on_tick=lambda e: reset_busy())
                    self.page.overlay.append(reset_timer)
                except:
                    import threading
                    import time
                    threading.Thread(target=lambda: (time.sleep((duration + 100) / 1000.0), reset_busy()), daemon=True).start()
                return

            # 4) Recordarme
            if getattr(self.ui, "remember", None) is not None and self.ui.remember.value:
                try:
                    self.page.client_storage.set("remember_username", user)
                except Exception:
                    pass  # Ignorar errores de storage
            else:
                try:
                    self.page.client_storage.remove("remember_username")
                except Exception:
                    pass  # Ignorar errores de storage

            # 5) Éxito - Mostrar animación de éxito y esperar antes de navegar
            # Asegurarse de que el overlay esté visible
            if self.loading_overlay not in self.page.overlay:
                self.page.overlay.append(self.loading_overlay)
            self.loading_overlay.visible = True
            self.loading_overlay.opacity = 1.0
            self.page.update()
            
            # Mostrar animación de éxito con callback para navegar después
            def continue_to_dashboard():
                try:
                    # Resetear estado de busy
                    self._busy = False
                    if getattr(self.ui, "login_btn", None) is not None:
                        self.ui.login_btn.disabled = False
                    
                    # Ocultar el overlay primero
                    self._remove_overlay()
                    
                    # Mostrar mensaje de éxito
                    self.show_info("¡Inicio de sesión exitoso!")
                    
                    # Cambiar de vista - usar run_task para asegurar que se ejecute en el hilo correcto
                    async def navigate():
                        self.continuar(usr)
                    
                    # Intentar usar run_task, si falla usar directamente
                    try:
                        self.page.run_task(navigate)
                    except:
                        # Fallback: ejecutar directamente
                        self.continuar(usr)
                except Exception as ex:
                    # Intentar navegar de todas formas
                    try:
                        self._remove_overlay()
                        self.continuar(usr)
                    except:
                        pass
            
            # Mostrar animación de éxito (dura 1.5 segundos por defecto)
            self.loading_overlay.show_success(duration=1500, callback=continue_to_dashboard)

        except Exception as ex:
            # Manejar errores inesperados en el procesamiento
            self._handle_search_error(ex)
