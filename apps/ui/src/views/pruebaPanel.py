# src/views/prueba_panel.py
import flet as ft
from .dashboard import Dashboard  # para back
from ..modules.pruebas.pruebasLogic import PruebaLogic, ViewModel, OptionData

def PruebaPanelUI(page: ft.Page, prueba_id: int) -> ft.Control:
    logic = PruebaLogic(prueba_id=prueba_id)

    if not logic.cargar():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("No se pudo cargar la prueba.", color=ft.Colors.RED),
                    ft.Text(f"ID: {prueba_id}", color=ft.Colors.GREY),
                    ft.ElevatedButton("Volver", on_click=lambda e: _back(page, logic))
                ],
                spacing=8,
            )
        )

    if not logic.questions:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(logic.data.get("titulo", ""), size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Esta prueba no tiene preguntas registradas.", color=ft.Colors.GREY),
                    ft.ElevatedButton("Volver", on_click=lambda e: _back(page, logic)),
                ],
                spacing=12,
            )
        )

    # ---- Estado UI (solo controles) ----
    page.title = f"Prueba #{logic.data.get('id')} – {logic.data.get('titulo')}"
    page.bgcolor = ft.Colors.GREY_100
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    progress_bar = ft.ProgressBar(value=0.0, height=6)
    progress_text = ft.Text("", size=12, color=ft.Colors.GREY)
    aciertos_text = ft.Text("", size=12, color=ft.Colors.GREEN)
    timer_icon = ft.Icon(ft.Icons.ALARM, size=16, color=ft.Colors.RED)
    timer_text = ft.Text("", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
    subtitle_text = ft.Text("", size=12, color=ft.Colors.GREY)
    title_text = ft.Text(logic.data.get("titulo", ""), weight=ft.FontWeight.BOLD, size=16)
    question_rich = ft.Text(spans=[], selectable=False)
    options_col = ft.Column(spacing=12)

    # ---- Render principal desde ViewModel ----
    def set_btn_label(btn: ft.ElevatedButton, vm: ViewModel):
        btn.text = "Siguiente" if vm.validada else "Validar"

    def option_card(opt: OptionData, vm: ViewModel) -> ft.Container:
        value_text = opt.text
        img_url = opt.image
        selected = (vm.seleccion_actual == value_text)
        validated = vm.validada

        border_color = ft.Colors.BLUE if selected else ft.Colors.GREY_300
        bg = ft.Colors.BLUE_50 if selected else ft.Colors.WHITE
        radio_fill = ft.Colors.BLUE if selected else ft.Colors.GREY_400

        # Feedback si ya se validó
        if validated:
            # Determinar corrección usando la lógica
            es_ok = _es_correcta_vm(value_text)
            if es_ok:
                border_color = ft.Colors.GREEN
                bg = ft.Colors.GREEN_50
                radio_fill = ft.Colors.GREEN
            elif selected and not es_ok:
                border_color = ft.Colors.RED
                bg = ft.Colors.RED_50
                radio_fill = ft.Colors.RED

        content_controls = [
            ft.Icon(
                name=ft.Icons.RADIO_BUTTON_CHECKED if selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                color=radio_fill,
            ),
            ft.Text(value_text, size=14, selectable=False, expand=True),
        ]
        if img_url:
            content_controls.append(ft.Image(src=img_url, height=42, fit=ft.ImageFit.CONTAIN))

        return ft.Container(
            bgcolor=bg,
            padding=12,
            border=ft.border.all(1, border_color),
            border_radius=12,
            ink=True,
            on_click=(None if validated else (lambda e, t=value_text: on_select(t))),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=content_controls,
            ),
        )

    def _es_correcta_vm(value_text: str) -> bool:
        # función pequeña que consulta a logic con el q actual
        q = logic.questions[logic.idx]
        return logic._es_correcta(q, value_text)

    def render(vm: ViewModel):
        progress_text.value = vm.progreso_txt
        progress_bar.value = vm.progreso_val

        subtitle_text.value = vm.enunciado
        spans = [ft.TextSpan(vm.enunciado + ("\n" if vm.secuencia else ""))]
        if vm.secuencia:
            spans.append(
                ft.TextSpan(
                    str(vm.secuencia),
                    style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                )
            )
        question_rich.spans = spans

        aciertos_text.value = f"Aciertos: {vm.aciertos} / {vm.total}"
        timer_text.value = vm.tiempo_mmss

        options_col.controls = [option_card(o, vm) for o in vm.opciones]
        set_btn_label(btn_next, vm)

        page.update()

    # ---- Handlers (UI -> lógica) ----
    def on_select(value_text: str):
        logic.seleccionar(value_text)
        render(logic.view())

    def on_prev(e):
        if logic.anterior():
            render(logic.view())

    def on_next(e):
        vm = logic.view()
        if not vm.validada:
            ok = logic.validar_actual()
            if not ok:
                _snack("Responde antes de validar.", ft.Colors.RED)
                return
            # feedback
            _snack("✅ ¡Correcto!" if _es_correcta_vm(vm.seleccion_actual or "") else "❌ Incorrecto",
                   ft.Colors.GREEN if _es_correcta_vm(vm.seleccion_actual or "") else ft.Colors.RED)
            render(logic.view())
            return
        # si ya estaba validada, avanzar o finalizar
        if not logic.siguiente():
            on_finish("finalizado por el usuario")
        render(logic.view())

    def on_finish(motivo: str):
        result = logic.finalizar(motivo)
        resumen = result.get("resumen", {})
        err = result.get("error")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Resultado de la prueba"),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(f"Correctas: {resumen.get('correctas', 0)}"),
                    ft.Text(f"Incorrectas: {resumen.get('incorrectas', 0)}"),
                    ft.Text(f"Sin responder: {resumen.get('pendientes', 0)}"),
                    ft.Text(f"Puntaje: {resumen.get('puntaje', 0.0):.1f}%"),
                    ft.Text(f"Estado: {resumen.get('motivo', motivo)}"),
                    *( [ft.Text(f"⚠️ Error guardando intento: {err}", color=ft.Colors.RED)] if err else [] )
                ],
            ),
            actions=[ft.TextButton("Volver al dashboard", on_click=lambda e: _back(page, logic))],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
        render(logic.view())

    def _snack(msg: str, color=None):
        page.snack_bar = ft.SnackBar(ft.Text(msg, color=color))
        page.snack_bar.open = True
        page.update()

    def _back(page: ft.Page, logic: PruebaLogic):
        logic.stop_timer()
        page.clean()
        Dashboard(page)
        page.update()

    # ---- UI Layout ----
    header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=ft.padding.symmetric(10, 12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: _back(page, logic)),
                title_text,
                ft.Container(width=40),
            ],
        ),
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
    )

    subheader = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        progress_text,
                        ft.Row(controls=[aciertos_text, ft.Container(width=10), timer_icon, timer_text], spacing=6),
                    ],
                ),
                progress_bar,
            ],
        ),
    )

    question_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=16,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Container(
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=12,
                    padding=16,
                    content=ft.Column(spacing=6, controls=[subtitle_text, question_rich]),
                ),
                options_col,
            ],
        ),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3)),
    )

    btn_prev = ft.ElevatedButton(
        text="Anterior",
        icon=ft.Icons.ARROW_BACK,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREY_200,
            color=ft.Colors.BLACK87,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(12, 16),
        ),
        on_click=on_prev,
    )
    btn_next = ft.ElevatedButton(
        text="Validar",
        icon=ft.Icons.ARROW_FORWARD,
        icon_color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(12, 16),
        ),
        on_click=on_next,
    )

    bottom_actions = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=12,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(content=btn_prev, expand=True),
                ft.Container(width=12),
                ft.Container(content=btn_next, expand=True),
            ],
        ),
    )

    center_wrapper = ft.Container(
        width=360,
        padding=12,
        content=ft.Column(spacing=12, controls=[header, subheader, question_card, bottom_actions]),
    )

    # ---- Primer render + timer ----
    render(logic.view())

    # Ticks: solo actualiza mm:ss en la UI
    def _tick():
        vm = logic.view()
        timer_text.value = vm.tiempo_mmss
        page.update()

    def _timeout():
        _snack("Tiempo agotado.")
        on_finish("tiempo agotado")

    page.run_task(logic.countdown, _tick, _timeout)
    return center_wrapper
