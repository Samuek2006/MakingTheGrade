# src/views/examView.py
from __future__ import annotations
import flet as ft
from typing import Optional
from ..modules.exams.examLogic import ExamLogic
from .nav_bar import build_navigation_bar
from .loading_overlay import LoadingOverlay


class ExamViewUI(ft.Column):
    """Vista dinámica para realizar pruebas/exámenes"""
    
    def __init__(self, page: ft.Page, exam_id: str, user: Optional[dict] = None, controller=None, exam_data: Optional[dict] = None):
        super().__init__(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        self.page = page
        self.exam_id = exam_id
        self.user = user or {}
        self.controller = controller
        self.logic = ExamLogic(exam_id=exam_id, exam_data=exam_data)
        
        # Cargar el examen
        exam_loaded = False
        error_msg = None
        try:
            exam_loaded = self.logic.load_exam()
            if not exam_loaded:
                error_msg = f"No se pudo cargar el examen con ID '{exam_id}'. Verifica que el ID sea correcto y que el examen exista en la API."
        except Exception as e:
            error_msg = f"Error al cargar el examen: {str(e)}"
            exam_loaded = False
        
        if not exam_loaded:
            # Construir UI básica para mostrar error
            self.page.title = "Error"
            self.page.adaptive = True
            self._build_error_ui(error_msg or "No se pudo cargar el examen.")
            return
        
        # Verificar que tenga preguntas
        if not self.logic.questions or len(self.logic.questions) == 0:
            self.page.title = "Error"
            self.page.adaptive = True
            self._build_error_ui("El examen no tiene preguntas disponibles.")
            return
        
        self.page.title = "Realizar Prueba"
        self.page.adaptive = True
        self.page.bgcolor = ft.Colors.GREY_50
        
        # Crear overlay de carga
        self.loading_overlay = LoadingOverlay(page=self.page, message="Procesando...")
        self.loading_overlay.visible = False
        
        # Temporizador para avance automático
        self.auto_advance_task = None
        self.auto_advance_cancelled = False
        
        # Controles principales mejorados y responsive
        self.title_text = ft.Text(
            "",
            size=18,  # Tamaño más pequeño para móvil
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            max_lines=2,  # Permitir múltiples líneas si es necesario
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.progress_text = ft.Text("", size=15, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500)
        self.progress_bar = ft.ProgressBar(
            value=0.0,
            height=8,
            bgcolor=ft.Colors.GREY_200,
            color=ft.Colors.BLUE_600,
            border_radius=4,
        )
        self.question_text = ft.Text(
            "",
            size=18,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.GREY_900,
        )
        self.options_column = ft.Column(spacing=14)
        self.result_container = ft.Container(visible=False)
        self.next_button = ft.ElevatedButton(
            text="Siguiente",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self._on_next_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=ft.padding.symmetric(16, 32),
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=2,
            ),
        )
        self.prev_button = ft.ElevatedButton(
            text="Anterior",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._on_prev_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_200,
                color=ft.Colors.GREY_800,
                padding=ft.padding.symmetric(16, 32),
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=1,
            ),
        )
        
        # Construir la UI
        self._build_ui()
        self._update_question()
    
    def _build_ui(self):
        """Construye la interfaz de usuario"""
        exam_info = self.logic.get_exam_info()
        self.title_text.value = exam_info.get("exam_name", "Prueba")
        
        # Header mejorado con gradiente y mejor diseño
        header = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_600, ft.Colors.BLUE_400],
            ),
            border_radius=ft.border_radius.only(
                bottom_left=20, bottom_right=20
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=16),  # Padding responsive
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self._go_back_with_loading(),
                        tooltip="Volver al dashboard",
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.WHITE24,
                            shape=ft.CircleBorder(),
                        ),
                    ),
                    ft.Container(
                        content=self.title_text,
                        expand=True,  # Se expande para ocupar el espacio disponible
                    ),
                    ft.Container(width=48),  # Espaciador para balancear
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 2),
            ),
        )
        
        # Barra de progreso mejorada y responsive
        progress_container = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=16, vertical=16),  # Padding responsive
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.progress_text,
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=18,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=8),
                    self.progress_bar,
                ],
                spacing=0,
            ),
            width=600,  # Ancho fijo para pantallas grandes
            border=ft.border.all(1, ft.Colors.GREY_200),
            shadow=ft.BoxShadow(
                blur_radius=4,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
        )
        
        # Contenedor de pregunta mejorado y responsive
        question_card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=20, vertical=20),  # Padding responsive
            content=ft.Column(
                controls=[
                    # Badge de número de pregunta
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.HELP_OUTLINE,
                                    size=20,
                                    color=ft.Colors.BLUE_600,
                                ),
                                ft.Text(
                                    "Pregunta",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_600,
                                ),
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=20,
                        width=120,
                    ),
                    ft.Container(height=16),
                    self.question_text,
                    ft.Container(height=20),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=20),
                    self.options_column,
                    ft.Container(height=12),
                    self.result_container,
                ],
                spacing=0,
            ),
            width=600,  # Ancho fijo para pantallas grandes
            border=ft.border.all(1, ft.Colors.GREY_200),
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
        )
        
        # Botones de navegación
        buttons_row = ft.Row(
            controls=[
                self.prev_button,
                ft.Container(width=12),
                self.next_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        buttons_container = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=16, vertical=16),  # Padding responsive
            content=buttons_row,
            width=600,  # Ancho fijo para pantallas grandes
            border=ft.border.all(1, ft.Colors.GREY_200),
            shadow=ft.BoxShadow(
                blur_radius=4,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
        )
        
        # Navbar
        navbar = build_navigation_bar(
            page=self.page,
            selected_index=0,
            on_change=None
        )
        
        # Contenido principal con scroll
        body_content = ft.Column(
            controls=[
                header,
                progress_container,
                question_card,
                buttons_container,
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Container del body con scroll independiente y responsive
        # El scroll debe estar en el Column interno, no en el Container
        body_container = ft.Container(
            expand=True,
            alignment=ft.alignment.top_center,
            padding=ft.padding.symmetric(horizontal=16, vertical=16),  # Padding responsive
            content=body_content,
            clip_behavior=ft.ClipBehavior.NONE,  # Permitir que el scroll funcione
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
    
    def _update_question(self):
        """Actualiza la UI con la pregunta actual"""
        question = self.logic.get_current_question()
        if not question:
            self._show_error("No hay preguntas disponibles.")
            return
        
        # Actualizar progreso
        progress = self.logic.get_progress()
        self.progress_text.value = f"Pregunta {progress['current']} de {progress['total']}"
        self.progress_bar.value = progress['progress_percent'] / 100
        
        # Actualizar pregunta
        question_text = question.get("text") or question.get("enunciado", "")
        self.question_text.value = question_text
        
        # Actualizar opciones
        options = question.get("options", {}) or question.get("opciones", {})
        
        # Validar que haya opciones
        if not options or not isinstance(options, dict) or len(options) == 0:
            self._show_error(f"La pregunta no tiene opciones válidas. Formato recibido: {type(options)}")
            return
        
        self.options_column.controls = []
        
        selected_answer = self.logic.selected_answer
        show_result = self.logic.show_result
        correct_answer = question.get("correct", "")
        
        # Obtener información de la respuesta del usuario si ya fue validada
        user_answer_data = self.logic.user_answers.get(self.logic.current_question_idx)
        is_correct = False
        if user_answer_data:
            is_correct = user_answer_data.get("correct", False)
        
        for key, value in options.items():
            option_text = str(value)
            is_selected = selected_answer == key
            is_correct_option = key.lower() == str(correct_answer).lower()
            
            # Determinar colores y estilo
            bg_color = ft.Colors.WHITE
            border_color = ft.Colors.GREY_300
            text_color = ft.Colors.BLACK87
            icon_name = ft.Icons.RADIO_BUTTON_UNCHECKED
            icon_color = ft.Colors.GREY
            
            if show_result:
                # Mostrar resultado
                if is_correct_option:
                    # Respuesta correcta (verde)
                    bg_color = ft.Colors.GREEN_50
                    border_color = ft.Colors.GREEN
                    icon_name = ft.Icons.CHECK_CIRCLE
                    icon_color = ft.Colors.GREEN
                elif is_selected and not is_correct:
                    # Respuesta incorrecta seleccionada (rojo)
                    bg_color = ft.Colors.RED_50
                    border_color = ft.Colors.RED
                    icon_name = ft.Icons.CANCEL
                    icon_color = ft.Colors.RED
            elif is_selected:
                # Opción seleccionada (azul)
                bg_color = ft.Colors.BLUE_50
                border_color = ft.Colors.BLUE
                icon_name = ft.Icons.RADIO_BUTTON_CHECKED
                icon_color = ft.Colors.BLUE
            
            # Badge de letra mejorado
            letter_badge = ft.Container(
                content=ft.Text(
                    key.upper(),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=border_color,
                ),
                width=40,
                height=40,
                alignment=ft.alignment.center,
                bgcolor=bg_color if bg_color != ft.Colors.WHITE else ft.Colors.GREY_50,
                border=ft.border.all(2, border_color),
                border_radius=20,
            )
            
            option_card = ft.Container(
                bgcolor=bg_color,
                border=ft.border.all(2, border_color),
                border_radius=16,
                padding=ft.padding.symmetric(horizontal=16, vertical=16),  # Padding responsive
                ink=True,
                on_click=None if show_result else (lambda e, k=key: self._on_option_click(k)),
                content=ft.Row(
                    controls=[
                        letter_badge,
                        ft.Container(width=12),  # Espaciador más pequeño en móvil
                        ft.Text(
                            option_text,
                            size=15,
                            color=text_color,
                            weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL,
                            expand=True,
                            max_lines=3,  # Permitir múltiples líneas en móvil
                            overflow=ft.TextOverflow.VISIBLE,
                        ),
                        ft.Icon(
                            name=icon_name,
                            color=icon_color,
                            size=24,  # Icono ligeramente más pequeño
                        ) if show_result or is_selected else ft.Container(width=24),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=False,
                ),
                shadow=ft.BoxShadow(
                    blur_radius=4 if is_selected else 0,
                    color=ft.Colors.BLACK12 if is_selected else ft.Colors.TRANSPARENT,
                    offset=ft.Offset(0, 2),
                ) if is_selected or show_result else None,
            )
            self.options_column.controls.append(option_card)
        
        # Mostrar resultado si está validado
        if show_result:
            self._show_result(is_correct, correct_answer, options.get(correct_answer, ""))
        else:
            self.result_container.visible = False
        
        # Actualizar botones con mejor diseño
        if show_result:
            if self.logic.is_last_question():
                self.next_button.text = "Finalizar Examen"
                self.next_button.icon = ft.Icons.CHECK_CIRCLE
                self.next_button.style.bgcolor = ft.Colors.GREEN_600
            else:
                self.next_button.text = "Siguiente Pregunta"
                self.next_button.icon = ft.Icons.ARROW_FORWARD
                self.next_button.style.bgcolor = ft.Colors.BLUE_600
        else:
            self.next_button.text = "Validar Respuesta"
            self.next_button.icon = ft.Icons.CHECK
            self.next_button.style.bgcolor = ft.Colors.BLUE_600
        
        # Deshabilitar botón siguiente si no hay respuesta seleccionada
        self.next_button.disabled = not selected_answer and not show_result
        
        self.page.update()
    
    def _show_result(self, is_correct: bool, correct_key: str, correct_text: str):
        """Muestra el resultado de la validación mejorado"""
        if is_correct:
            result_content = ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE,
                        size=32,
                        color=ft.Colors.GREEN_700,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "¡Correcto!",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700,
                            ),
                            ft.Text(
                                "Bien hecho, continúa así",
                                size=13,
                                color=ft.Colors.GREEN_600,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            bg_color = ft.Colors.GREEN_50
            border_color = ft.Colors.GREEN_700
        else:
            result_content = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CANCEL,
                                size=32,
                                color=ft.Colors.RED_700,
                            ),
                            ft.Text(
                                "Incorrecto",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_700,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.LIGHTBULB_OUTLINE,
                                    size=20,
                                    color=ft.Colors.ORANGE_700,
                                ),
                                ft.Text(
                                    f"La respuesta correcta es: {correct_key.upper()}. {correct_text}",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.GREY_800,
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=12,
                        bgcolor=ft.Colors.ORANGE_50,
                        border_radius=12,
                    ),
                ],
                spacing=0,
            )
            bg_color = ft.Colors.RED_50
            border_color = ft.Colors.RED_700
        
        self.result_container.content = ft.Container(
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=16,
            padding=20,
            content=result_content,
        )
        self.result_container.visible = True
    
    def _on_option_click(self, option_key: str):
        """Maneja el click en una opción"""
        if not self.logic.show_result:
            self.logic.select_answer(option_key)
            self._update_question()
    
    def _on_next_click(self, e):
        """Maneja el click en el botón siguiente"""
        if not self.logic.show_result:
            # Validar respuesta
            if not self.logic.validate_and_show_result():
                self._show_snackbar("Por favor selecciona una respuesta antes de validar.", ft.Colors.ORANGE)
                return
            
            # Mostrar animación de carga al validar
            self._show_loading("Validando respuesta...")
            
            # Actualizar después de un pequeño delay
            import asyncio
            async def update_after_validation():
                await asyncio.sleep(0.4)  # Pequeño delay para mostrar la animación
                self._update_question()
                self._hide_loading()
                
                # Iniciar temporizador automático para avanzar después de 2.5 segundos
                self._start_auto_advance()
            
            try:
                self.page.run_task(update_after_validation)
            except Exception:
                # Fallback si falla run_task
                import threading
                import time
                def delayed_update():
                    time.sleep(0.4)
                    self._update_question()
                    self._hide_loading()
                    # Iniciar temporizador automático
                    self._start_auto_advance()
                threading.Thread(target=delayed_update, daemon=True).start()
        else:
            # Cancelar el avance automático si el usuario hace clic manualmente
            self._cancel_auto_advance()
            
            # Continuar a la siguiente pregunta o finalizar
            if self.logic.is_last_question():
                self._finish_exam()
            else:
                # Mostrar animación de carga al cambiar de pregunta
                self._show_loading("Cargando siguiente pregunta...")
                
                # Actualizar después de un pequeño delay
                import asyncio
                async def update_after_navigation():
                    await asyncio.sleep(0.4)  # Pequeño delay para mostrar la animación
                    if self.logic.continue_after_result():
                        self._update_question()
                    else:
                        self._finish_exam()
                    self._hide_loading()
                
                try:
                    self.page.run_task(update_after_navigation)
                except Exception:
                    # Fallback si falla run_task
                    import threading
                    import time
                    def delayed_navigate():
                        time.sleep(0.4)
                        if self.logic.continue_after_result():
                            self._update_question()
                        else:
                            self._finish_exam()
                        self._hide_loading()
                    threading.Thread(target=delayed_navigate, daemon=True).start()
    
    def _start_auto_advance(self):
        """Inicia el temporizador automático para avanzar a la siguiente pregunta"""
        # Cancelar cualquier temporizador anterior
        self._cancel_auto_advance()
        self.auto_advance_cancelled = False
        
        import asyncio
        async def auto_advance():
            # Esperar 2.5 segundos
            await asyncio.sleep(2.5)
            
            # Verificar que no se haya cancelado
            if not self.auto_advance_cancelled and self.logic.show_result:
                # Avanzar automáticamente a la siguiente pregunta
                if self.logic.is_last_question():
                    self._finish_exam()
                else:
                    # Mostrar animación de carga al cambiar de pregunta
                    self._show_loading("Cargando siguiente pregunta...")
                    
                    # Actualizar después de un pequeño delay
                    async def update_after_navigation():
                        await asyncio.sleep(0.4)
                        if self.logic.continue_after_result():
                            self._update_question()
                            # Reiniciar el temporizador para la siguiente pregunta si es necesario
                            # (solo si se valida automáticamente, pero aquí ya avanzamos)
                        else:
                            self._finish_exam()
                        self._hide_loading()
                    
                    try:
                        self.page.run_task(update_after_navigation)
                    except Exception:
                        # Fallback
                        import threading
                        import time
                        def delayed_navigate():
                            time.sleep(0.4)
                            if self.logic.continue_after_result():
                                self._update_question()
                            else:
                                self._finish_exam()
                            self._hide_loading()
                        threading.Thread(target=delayed_navigate, daemon=True).start()
        
        try:
            self.auto_advance_task = self.page.run_task(auto_advance)
        except Exception:
            # Fallback si falla run_task
            import threading
            import time
            def delayed_advance():
                time.sleep(2.5)
                if not self.auto_advance_cancelled and self.logic.show_result:
                    if self.logic.is_last_question():
                        self._finish_exam()
                    else:
                        if self.logic.continue_after_result():
                            self._update_question()
                        else:
                            self._finish_exam()
            threading.Thread(target=delayed_advance, daemon=True).start()
    
    def _cancel_auto_advance(self):
        """Cancela el temporizador automático"""
        self.auto_advance_cancelled = True
        # Nota: No podemos cancelar directamente la tarea de asyncio desde aquí,
        # pero la bandera auto_advance_cancelled evitará que se ejecute
    
    def _on_prev_click(self, e):
        """Maneja el click en el botón anterior"""
        # Cancelar el avance automático si está activo
        self._cancel_auto_advance()
        
        if self.logic.previous_question():
            # Mostrar animación de carga al cambiar de pregunta
            self._show_loading("Cargando pregunta anterior...")
            
            # Actualizar después de un pequeño delay
            import asyncio
            async def update_after_navigation():
                await asyncio.sleep(0.4)  # Pequeño delay para mostrar la animación
                self._update_question()
                self._hide_loading()
            
            try:
                self.page.run_task(update_after_navigation)
            except Exception:
                # Fallback si falla run_task
                import threading
                import time
                def delayed_update():
                    time.sleep(0.4)
                    self._update_question()
                    self._hide_loading()
                threading.Thread(target=delayed_update, daemon=True).start()
    
    def _finish_exam(self):
        """Finaliza el examen y muestra los resultados"""
        # Cancelar el avance automático si está activo
        self._cancel_auto_advance()
        
        # Ocultar loading si está activo
        self._hide_loading()
        
        # Calcular el puntaje final
        score = self.logic.get_final_score()
        
        # Crear diálogo con los resultados
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Examen Finalizado", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Divider(),
                    ft.Text(f"Preguntas totales: {score['total']}", size=14),
                    ft.Text(
                        f"✅ Correctas: {score['correct']}",
                        size=14,
                        color=ft.Colors.GREEN,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"❌ Incorrectas: {score['incorrect']}",
                        size=14,
                        color=ft.Colors.RED,
                    ),
                    ft.Text(
                        f"⏭️ Sin responder: {score['unanswered']}",
                        size=14,
                        color=ft.Colors.GREY,
                    ),
                    ft.Divider(),
                    ft.Text(
                        f"Puntaje: {score['score_percent']:.1f}%",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                    ),
                    ft.Text(
                        f"Puntos obtenidos: {score['earned_points']:.1f} / {score['total_points']}",
                        size=14,
                    ),
                ],
                spacing=8,
                height=300,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    "Volver al Dashboard",
                    on_click=self._go_back_from_dialog,
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _go_back_from_dialog(self, e=None):
        """Cierra el diálogo y regresa al dashboard"""
        # Cerrar el diálogo primero
        try:
            if self.page.dialog:
                self.page.dialog.open = False
                self.page.update()
        except Exception:
            pass
        
        # Mostrar animación de carga
        self._show_loading("Regresando al dashboard...")
        
        # Pequeño delay para mostrar la animación, luego regresar
        import asyncio
        async def go_back_after_delay():
            await asyncio.sleep(0.5)
            # No ocultar loading aquí, se ocultará cuando cambie la vista
            self._go_back()
        
        try:
            self.page.run_task(go_back_after_delay)
        except Exception:
            # Fallback si falla run_task
            import threading
            import time
            def delayed_go_back():
                time.sleep(0.5)
                # No ocultar loading aquí, se ocultará cuando cambie la vista
                self._go_back()
            threading.Thread(target=delayed_go_back, daemon=True).start()
    
    def _go_back_with_loading(self):
        """Regresa al dashboard con animación de carga"""
        # Mostrar animación de carga
        self._show_loading("Regresando al dashboard...")
        
        # Pequeño delay para mostrar la animación, luego regresar
        import asyncio
        async def go_back_after_delay():
            await asyncio.sleep(0.5)
            # No ocultar loading aquí, se ocultará cuando cambie la vista
            self._go_back()
        
        try:
            self.page.run_task(go_back_after_delay)
        except Exception:
            # Fallback si falla run_task
            import threading
            import time
            def delayed_go_back():
                time.sleep(0.5)
                # No ocultar loading aquí, se ocultará cuando cambie la vista
                self._go_back()
            threading.Thread(target=delayed_go_back, daemon=True).start()
    
    def _go_back(self, e=None):
        """Regresa al dashboard"""
        try:
            # Ocultar loading antes de cambiar de vista
            self._hide_loading()
            
            if self.controller and hasattr(self.controller, "show_dashboard"):
                # Usar el controller para navegar de vuelta
                self.controller.show_dashboard(user_obj=self.user)
            else:
                # Fallback si no hay controller
                try:
                    if self.page:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Error: No se puede navegar sin controller"),
                            bgcolor=ft.Colors.RED,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                except Exception:
                    pass
        except Exception as ex:
            try:
                self._hide_loading()
                if self.page:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error al regresar: {str(ex)}"),
                        bgcolor=ft.Colors.RED,
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception:
                pass
    
    def _build_error_ui(self, message: str):
        """Construye la UI de error"""
        error_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED),
                    ft.Text(message, size=16, color=ft.Colors.RED, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        "Volver al Dashboard",
                        on_click=self._go_back,
                        icon=ft.Icons.ARROW_BACK,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=40,
            alignment=ft.alignment.center,
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
        
        # Estructura final: Column con contenido y navbar fijo
        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=error_container,
            ),
            navbar_container  # Navbar fijo (sin expand, queda abajo)
        ]
        self.page.update()
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error (método legacy)"""
        self._build_error_ui(message)
    
    def _show_snackbar(self, message: str, color=None):
        """Muestra un snackbar"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_loading(self, message: str = "Procesando..."):
        """Muestra el overlay de carga"""
        if self.loading_overlay not in self.page.overlay:
            self.page.overlay.append(self.loading_overlay)
            self.page.update()
        
        self.loading_overlay.update_message(message)
        self.loading_overlay.visible = True
        self.loading_overlay.show()
        self.page.update()
    
    def _hide_loading(self):
        """Oculta el overlay de carga"""
        try:
            if not self.page:
                return
            
            if hasattr(self, 'loading_overlay') and self.loading_overlay:
                self.loading_overlay.hide()
                
                # Remover del overlay de la página
                if hasattr(self.page, 'overlay') and self.loading_overlay in self.page.overlay:
                    self.page.overlay.remove(self.loading_overlay)
                
                self.page.update()
        except Exception:
            # Ignorar errores si la página ya cambió de vista
            pass

