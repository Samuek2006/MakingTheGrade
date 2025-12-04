# src/views/dashboard.py
from __future__ import annotations
import flet as ft
from typing import List, Dict, Any, Optional
from .nav_bar import build_navigation_bar
from .loading_overlay import LoadingOverlay


class DashboardUI(ft.Column):
    def __init__(self, page: ft.Page, user: Optional[dict] = None, logic: Optional[object] = None, controller=None):
        super().__init__(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        self.page = page
        self.user = user or {}
        self.logic = logic
        self.controller = controller
        
        # Crear overlay de carga
        self.loading_overlay = LoadingOverlay(page=self.page, message="Cargando examen...")
        self.loading_overlay.visible = False

        self.page.adaptive = True
        self.page.title = "Home"
        self.page.bgcolor = ft.Colors.GREY_50

        # ======== Contenido principal ========
        # Header mejorado con gradiente y mejor diseño
        header_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.QUIZ, size=28, color=ft.Colors.WHITE),
                            ft.Text(
                                "Pruebas Disponibles",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Text(
                        "Selecciona una prueba para comenzar",
                        size=14,
                        color=ft.Colors.WHITE70,
                    ),
                ],
                spacing=4,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_600, ft.Colors.BLUE_400],
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=20),
            border_radius=ft.border_radius.only(
                bottom_left=20, bottom_right=20
            ),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 2),
            ),
        )

        # factory de tarjeta mejorada con diseño moderno y responsive
        def card(titulo: str, subtitulo: str | None, bg, on_click):
            return ft.Container(
                content=ft.Row(
                    controls=[
                        # Icono con fondo circular
                        ft.Container(
                            content=ft.Icon(
                                name=ft.Icons.QUIZ,
                                color=ft.Colors.BLUE_600,
                                size=28,
                            ),
                            bgcolor=ft.Colors.BLUE_50,
                            width=56,
                            height=56,
                            border_radius=28,
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(width=16),  # Espaciador
                        ft.Column(
                            [
                                ft.Text(
                                    titulo,
                                    weight=ft.FontWeight.BOLD,
                                    size=17,
                                    color=ft.Colors.GREY_900,
                                ),
                                ft.Text(
                                    subtitulo or "Sin descripción",
                                    size=13,
                                    color=ft.Colors.GREY_600,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=4,
                            expand=True,
                        ),
                        ft.Icon(
                            name=ft.Icons.CHEVRON_RIGHT,
                            color=ft.Colors.GREY_400,
                            size=24,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=0,
                ),
                bgcolor=bg,
                border_radius=16,
                padding=20,
                ink=True,
                on_click=on_click,
                width=500,  # Ancho fijo para pantallas grandes
                border=ft.border.all(1, ft.Colors.GREY_200),
                shadow=ft.BoxShadow(
                    blur_radius=4,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            )

        # Construye la lista de tarjetas desde la data
        def build_cards(pruebas: List[Dict[str, Any]] | None):
            items: List[ft.Control] = []
            if not pruebas:
                # Estado vacío mejorado y responsive
                items.append(
                    ft.Container(
                        padding=40,
                        border_radius=20,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(2, ft.Colors.GREY_300, ft.BorderStyle.DASHED),
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.INBOX,
                                    size=64,
                                    color=ft.Colors.GREY_400,
                                ),
                                ft.Container(height=16),
                                ft.Text(
                                    "Aún no hay pruebas disponibles",
                                    weight=ft.FontWeight.BOLD,
                                    size=18,
                                    color=ft.Colors.GREY_700,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Las pruebas aparecerán aquí cuando estén disponibles",
                                    size=14,
                                    color=ft.Colors.GREY_500,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=500,  # Ancho fijo para pantallas grandes
                    )
                )
                return items

            for p in pruebas:
                exam_id = p.get("id")
                # Asegurarse de que el ID sea válido
                if exam_id is None:
                    continue
                
                # Convertir a string para asegurar compatibilidad
                exam_id_str = str(exam_id)
                exam_full_data = p.get("full_data")  # Obtener datos completos
                
                # Función auxiliar para capturar el exam_id y datos correctamente
                def make_click_handler(eid, full_data):
                    def handler(e):
                        self._open_exam(eid, full_data)
                    return handler
                
                items.append(
                    card(
                        titulo=p.get("titulo", "Prueba"),
                        subtitulo=p.get("descripcion", ""),
                        bg=ft.Colors.WHITE,
                        on_click=make_click_handler(exam_id_str, exam_full_data),
                    )
                )
            return items

        # Intentar traer pruebas si hay lógica; si no, mostrar vacío
        pruebas = None
        if self.logic and hasattr(self.logic, "cargaPruebas"):
            try:
                pruebas = self.logic.cargaPruebas()
            except Exception:
                pruebas = None

        # Contenido principal con scroll mejorado y responsive
        # Envolver cada tarjeta en un contenedor que se adapte al ancho
        cards_list = []
        for card_item in build_cards(pruebas):
            cards_list.append(
                ft.Container(
                    content=card_item,
                    alignment=ft.alignment.center,
                )
            )
        
        body_content = ft.Column(
            controls=[header_container, *cards_list],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # Container del body con scroll independiente y responsive
        # El scroll debe estar en el Column interno, no en el Container
        body_container = ft.Container(
            expand=True,
            alignment=ft.alignment.top_center,
            content=body_content,
            padding=ft.padding.only(left=16, right=16, top=0, bottom=16),
            clip_behavior=ft.ClipBehavior.NONE,  # Permitir que el scroll funcione
        )

        # Navbar
        navbar = build_navigation_bar(
            page=self.page,
            selected_index=0,
            on_change=None
        )

        # Navbar fijo en la parte inferior con división clara mejorada
        navbar_container = ft.Container(
            content=navbar,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(
                top=ft.border.BorderSide(1, ft.Colors.GREY_300)
            ),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, -2),
            ),
        )

        # Estructura final: Column con contenido scrolleable y navbar fijo
        self.controls = [
            body_container,  # Contenido con scroll (expand=True)
            navbar_container  # Navbar fijo (sin expand, queda abajo)
        ]

        self.page.update()
    
    def _open_exam(self, exam_id: str, exam_data: dict = None):
        """Abre la vista de examen para realizar la prueba"""
        if not exam_id:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("ID de examen no válido"),
                bgcolor=ft.Colors.RED,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Mostrar loading overlay
        self._show_loading()
        
        # Si no tenemos los datos completos, intentar obtenerlos de la lógica
        if not exam_data and self.logic:
            exam_data = self.logic.get_exam_data(exam_id)
        
        # Usar una pequeña demora para que se vea la animación
        def navigate():
            try:
                # Usar el controller para navegar
                if self.controller and hasattr(self.controller, "show_exam"):
                    self.controller.show_exam(exam_id=str(exam_id), user_obj=self.user, exam_data=exam_data)
                    # Ocultar loading después de navegar
                    self._hide_loading()
                else:
                    # Fallback si no hay controller
                    self._hide_loading()
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Error: No se puede navegar sin controller"),
                        bgcolor=ft.Colors.RED,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception:
                self._hide_loading()
        
        # Pequeño delay para mostrar la animación usando función asíncrona
        import asyncio
        async def delayed_navigate():
            await asyncio.sleep(0.3)
            navigate()
        
        # Ejecutar la función asíncrona
        try:
            self.page.run_task(delayed_navigate)
        except Exception:
            # Fallback: usar threading y page.run_on_idle si está disponible
            import threading
            import time
            def delayed_navigate_sync():
                time.sleep(0.3)
                if hasattr(self.page, "run_on_idle"):
                    self.page.run_on_idle(navigate)
                else:
                    navigate()
            threading.Thread(target=delayed_navigate_sync, daemon=True).start()
    
    def _show_loading(self):
        """Muestra el overlay de carga"""
        if self.loading_overlay not in self.page.overlay:
            self.page.overlay.append(self.loading_overlay)
            self.page.update()
        
        self.loading_overlay.visible = True
        self.loading_overlay.show()
        self.page.update()
    
    def _hide_loading(self):
        """Oculta el overlay de carga"""
        try:
            self.loading_overlay.hide()
            self.page.update()
            if self.loading_overlay in self.page.overlay:
                self.page.overlay.remove(self.loading_overlay)
            self.page.update()
        except Exception:
            pass
