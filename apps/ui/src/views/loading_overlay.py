import flet as ft

class LoadingOverlay(ft.Container):
    """Overlay de carga animado para mostrar durante el proceso de login"""
    
    def __init__(self, page: ft.Page, message: str = "Verificando credenciales..."):
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        PRIMARY = getattr(C, "BLUE_700", getattr(C, "BLUE", None))
        ERROR_COLOR = getattr(C, "RED_600", getattr(C, "RED", None))
        # Fondo transparente con blur (usando opacidad muy baja)
        BG_OVERLAY = ft.colors.with_opacity(0.3, getattr(C, "BLACK", "#000000")) if hasattr(ft, "colors") else "#0000004D"
        
        self.page = page
        self.message = message
        self._is_error = False
        
        # Spinner animado
        self.spinner = ft.ProgressRing(
            width=64,
            height=64,
            stroke_width=6,
            color=PRIMARY,
        )
        
        # Color de éxito (verde)
        SUCCESS_COLOR = getattr(C, "GREEN_600", getattr(C, "GREEN", None))
        
        # Icono de error (X) - inicialmente oculto
        self.error_icon = ft.Container(
            width=64,
            height=64,
            border_radius=32,
            bgcolor=ERROR_COLOR,
            content=ft.Icon(
                ft.Icons.CLOSE_ROUNDED,
                size=36,
                color=getattr(C, "WHITE", "#FFFFFF"),
            ),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            scale=0.0,
            visible=False,
        )
        
        # Icono de éxito (check) - inicialmente oculto
        self.success_icon = ft.Container(
            width=64,
            height=64,
            border_radius=32,
            bgcolor=SUCCESS_COLOR,
            content=ft.Icon(
                ft.Icons.CHECK_ROUNDED,
                size=36,
                color=getattr(C, "WHITE", "#FFFFFF"),
            ),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            scale=0.0,
            visible=False,
        )
        
        # Texto de carga con fondo semitransparente para mejor legibilidad
        self.loading_text = ft.Text(
            message,
            size=16,
            weight=ft.FontWeight.W_500,
            color=getattr(C, "GREY_800", "#1F2937"),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Contenido central sin Card, solo el spinner/error/éxito y texto
        self.content_column = ft.Column(
            [
                ft.Stack(
                    [
                        self.spinner,
                        self.error_icon,
                        self.success_icon,
                    ],
                    width=64,
                    height=64,
                ),
                ft.Container(height=20),
                self.loading_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            tight=True,
        )
        
        # Container principal con fondo semitransparente (sin Card blanco)
        # El overlay es solo visual, no bloquea la interacción porque no tiene eventos
        super().__init__(
            expand=True,
            bgcolor=BG_OVERLAY,
            alignment=ft.alignment.center,
            content=self.content_column,
            opacity=0.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            # Asegurar que esté por encima de todo
            left=0,
            top=0,
            right=0,
            bottom=0,
        )
        
    def show(self):
        """Muestra el overlay con animación"""
        self.opacity = 1.0
        # No hacer self.update() aquí - el código que llama debe hacer page.update()
        
    def hide(self):
        """Oculta el overlay con animación"""
        self.opacity = 0.0
        # Resetear estado de error y éxito
        self._is_error = False
        self.error_icon.visible = False
        self.error_icon.scale = 0.0
        self.success_icon.visible = False
        self.success_icon.scale = 0.0
        self.spinner.visible = True
        # Restaurar color y peso del texto
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        self.loading_text.color = getattr(C, "GREY_800", "#1F2937")
        self.loading_text.weight = ft.FontWeight.W_500
        # No hacer self.update() aquí - el código que llama debe hacer page.update()
        
    def update_message(self, new_message: str):
        """Actualiza el mensaje de carga"""
        self.loading_text.value = new_message
        self.message = new_message
        # No hacer self.update() aquí - el código que llama debe hacer page.update()
    
    def show_error(self, duration: int = 2000):
        """Muestra un error con X roja y mensaje 'Credenciales Inválidas'"""
        # Asegurarse de que el overlay esté en la página y visible
        if self not in self.page.overlay:
            self.page.overlay.append(self)
        self.visible = True
        self.opacity = 1.0
        
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        ERROR_COLOR = getattr(C, "RED_600", getattr(C, "RED", None))
        
        self._is_error = True
        # Ocultar spinner
        self.spinner.visible = False
        # Mostrar icono de error con animación
        self.error_icon.visible = True
        self.error_icon.scale = 1.0
        # Cambiar mensaje
        self.loading_text.value = "Credenciales Inválidas"
        self.loading_text.color = ERROR_COLOR
        self.loading_text.weight = ft.FontWeight.W_600
        
        # Forzar actualización múltiple
        self.page.update()
        self.page.update()
        
        # Auto-ocultar después de la duración especificada
        def auto_hide(e=None):
            try:
                self.hide()
                self.page.update()
                # Remover del overlay después de ocultar
                if self in self.page.overlay:
                    self.page.overlay.remove(self)
                self.page.update()
            except:
                pass
        
        try:
            hide_timer = ft.Timer(interval=duration, once=True, on_tick=auto_hide)
            self.page.overlay.append(hide_timer)
        except:
            # Si el timer falla, usar threading
            import threading
            def delayed_hide():
                import time
                time.sleep(duration / 1000.0)
                try:
                    self.page.run_task(auto_hide)
                except:
                    auto_hide()
            threading.Thread(target=delayed_hide, daemon=True).start()
    
    def show_success(self, duration: int = 1500, callback=None):
        """Muestra un éxito con check verde y mensaje '¡Inicio de sesión exitoso!'"""
        # Asegurarse de que el overlay esté en la página y visible
        if self not in self.page.overlay:
            self.page.overlay.append(self)
        self.visible = True
        self.opacity = 1.0
        
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        SUCCESS_COLOR = getattr(C, "GREEN_600", getattr(C, "GREEN", None))
        
        # Ocultar spinner
        self.spinner.visible = False
        # Ocultar icono de error si estaba visible
        self.error_icon.visible = False
        self.error_icon.scale = 0.0
        # Mostrar icono de éxito con animación
        self.success_icon.visible = True
        self.success_icon.scale = 1.0
        # Cambiar mensaje
        self.loading_text.value = "¡Inicio de sesión exitoso!"
        self.loading_text.color = SUCCESS_COLOR
        self.loading_text.weight = ft.FontWeight.W_600
        
        # Forzar actualización múltiple
        self.page.update()
        self.page.update()
        
        # Ejecutar callback después de la duración especificada (sin ocultar el overlay)
        # El overlay se ocultará cuando se cambie de vista en el callback
        def execute_callback(e=None):
            try:
                # Ejecutar callback si se proporcionó (que cambiará de vista y ocultará el overlay)
                if callback:
                    callback()
            except Exception:
                pass
        
        try:
            callback_timer = ft.Timer(interval=duration, once=True, on_tick=execute_callback)
            self.page.overlay.append(callback_timer)
        except:
            # Si el timer falla, usar threading
            import threading
            def delayed_callback():
                import time
                time.sleep(duration / 1000.0)
                try:
                    self.page.run_task(execute_callback)
                except:
                    execute_callback()
            threading.Thread(target=delayed_callback, daemon=True).start()

