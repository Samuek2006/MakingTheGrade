import flet as ft

class LoadingOverlay(ft.Container):
    """Overlay de carga animado para mostrar durante el proceso de login"""
    
    def __init__(self, page: ft.Page, message: str = "Verificando credenciales..."):
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        PRIMARY = getattr(C, "BLUE_700", getattr(C, "BLUE", None))
        # Fondo transparente con blur (usando opacidad muy baja)
        BG_OVERLAY = ft.colors.with_opacity(0.3, getattr(C, "BLACK", "#000000")) if hasattr(ft, "colors") else "#0000004D"
        
        self.page = page
        self.message = message
        
        # Spinner animado
        self.spinner = ft.ProgressRing(
            width=64,
            height=64,
            stroke_width=6,
            color=PRIMARY,
        )
        
        # Texto de carga con fondo semitransparente para mejor legibilidad
        self.loading_text = ft.Text(
            message,
            size=16,
            weight=ft.FontWeight.W_500,
            color=getattr(C, "GREY_800", "#1F2937"),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Contenido central sin Card, solo el spinner y texto
        content_column = ft.Column(
            [
                self.spinner,
                ft.Container(height=20),
                self.loading_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            tight=True,
        )
        
        # Container principal con fondo semitransparente (sin Card blanco)
        super().__init__(
            expand=True,
            bgcolor=BG_OVERLAY,
            alignment=ft.alignment.center,
            content=content_column,
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
        # No hacer self.update() aquí - el código que llama debe hacer page.update()
        
    def update_message(self, new_message: str):
        """Actualiza el mensaje de carga"""
        self.loading_text.value = new_message
        self.message = new_message
        # No hacer self.update() aquí - el código que llama debe hacer page.update()

