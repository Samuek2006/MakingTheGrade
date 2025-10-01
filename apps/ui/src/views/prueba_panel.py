# views/prueba_panel.py
import flet as ft
from datetime import timedelta
import asyncio

def build_prueba_panel(page: ft.Page, prueba_id: int) -> ft.Container:
    # Import local para evitar import circular
    from ..components.crud import get_prueba_con_preguntas

    data = get_prueba_con_preguntas(prueba_id)
    if not data:
        return ft.Container(
            content=ft.Column([
                ft.Text("No se pudo cargar la prueba.", color=ft.Colors.RED),
                ft.Text(f"ID: {prueba_id}", color=ft.Colors.GREY),
            ], spacing=8)
        )

    page.title = f"Prueba #{data['id']} – {data['titulo']}"
    questions = []

    # Normaliza a la estructura que usa tu UI
    for p in data["preguntas"]:
        questions.append({
            "titulo": data["titulo"],
            "enunciado": p.get("enunciado", ""),
            "secuencia": p.get("secuencia", None),
            "opciones": p.get("opciones", []),
            "correcta": p.get("correcta", None),
        })

    if not questions:
        return ft.Container(
            content=ft.Column([
                ft.Text(data["titulo"], size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Esta prueba no tiene preguntas registradas.", color=ft.Colors.GREY),
                ft.ElevatedButton("Volver", on_click=lambda e: _back(page)),
            ], spacing=12)
        )

    # Estado UI
    idx = {"value": 0}
    seleccion = {"value": None}
    # Duración: usa la de la BD si existe, sino 9m 30s por defecto
    total_seconds = data["duracion_seg"] if data["duracion_seg"] else (9 * 60 + 30)
    remaining = {"value": total_seconds}
    stop_timer = {"value": False}

    progress_bar = ft.ProgressBar(value=0.0, height=6)
    progress_text = ft.Text("", size=12, color=ft.Colors.GREY)
    timer_icon = ft.Icon(ft.Icons.ALARM, size=16, color=ft.Colors.RED)
    timer_text = ft.Text("", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
    subtitle_text = ft.Text("", size=12, color=ft.Colors.GREY)
    title_text = ft.Text(data["titulo"], weight=ft.FontWeight.BOLD, size=16)

    question_rich = ft.Text(spans=[], selectable=False)
    options_col = ft.Column(spacing=12)

    def update_timer_label():
        t = str(timedelta(seconds=remaining["value"]))
        mm_ss = t.split(":")[1] + ":" + t.split(":")[2].zfill(2)
        timer_text.value = mm_ss

    def option_card(texto: str) -> ft.Container:
        selected = (seleccion["value"] == texto)
        border_color = ft.Colors.BLUE if selected else ft.Colors.GREY_300
        bg = ft.Colors.BLUE_50 if selected else ft.Colors.WHITE
        radio_fill = ft.Colors.BLUE if selected else ft.Colors.GREY_400
        return ft.Container(
            bgcolor=bg,
            padding=12,
            border=ft.border.all(1, border_color),
            border_radius=12,
            ink=True,
            on_click=lambda e, t=texto: select_option(t),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                spacing=12,
                controls=[
                    ft.Icon(
                        name=ft.Icons.RADIO_BUTTON_CHECKED if selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        color=radio_fill
                    ),
                    ft.Text(texto, size=14),
                ]
            )
        )

    def hydrate():
        q = questions[idx["value"]]
        total = len(questions)

        progress_text.value = f"Pregunta {idx['value'] + 1} de {total}"
        progress_bar.value = (idx["value"] + 1) / total

        subtitle_text.value = q["enunciado"]
        # Construir spans del enunciado/secuencia
        spans = [ft.TextSpan(q["enunciado"] + ("\n" if q.get("secuencia") else ""))]
        if q.get("secuencia"):
            spans.append(
                ft.TextSpan(
                    str(q["secuencia"]),
                    style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                )
            )
        question_rich.spans = spans

        options_col.controls = [option_card(o) for o in (q["opciones"] or [])]
        update_timer_label()
        page.update()

    def select_option(value: str):
        seleccion["value"] = value
        hydrate()

    def prev_question(e):
        if idx["value"] > 0:
            idx["value"] -= 1
            seleccion["value"] = None
            hydrate()

    def next_question(e):
        if idx["value"] < len(questions) - 1:
            idx["value"] += 1
            seleccion["value"] = None
            hydrate()
        else:
            # Fin de prueba
            stop_timer["value"] = True
            page.snack_bar = ft.SnackBar(ft.Text("Has finalizado la prueba."))
            page.snack_bar.open = True
            page.update()

    async def countdown():
        while remaining["value"] > 0 and not stop_timer["value"]:
            await asyncio.sleep(1)
            remaining["value"] -= 1
            update_timer_label()
            page.update()
        if remaining["value"] <= 0 and not stop_timer["value"]:
            page.snack_bar = ft.SnackBar(ft.Text("Tiempo agotado."))
            page.snack_bar.open = True
            page.update()

    def _back(page: ft.Page):
        stop_timer["value"] = True
        page.clean()
        from .dashboard import Dashboard
        Dashboard(page)
        page.update()

    def go_back_to_dashboard(e):
        _back(page)

    # ---- UI ----
    page.bgcolor = ft.Colors.GREY_100
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    header = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=ft.padding.symmetric(10, 12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back_to_dashboard),
                title_text,
                ft.Container(width=40),
            ]
        ),
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2))
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
                        ft.Row(controls=[timer_icon, timer_text], spacing=6),
                    ],
                ),
                progress_bar,
            ]
        )
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
                    content=ft.Column(spacing=6, controls=[subtitle_text, question_rich])
                ),
                options_col,
            ],
        ),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12, offset=ft.Offset(0, 3))
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
        on_click=prev_question
    )
    btn_next = ft.ElevatedButton(
        text="Siguiente",
        icon=ft.Icons.ARROW_FORWARD,
        icon_color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(12, 16),
        ),
        on_click=next_question
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
            ]
        )
    )

    center_wrapper = ft.Container(
        width=360,
        padding=12,
        content=ft.Column(
            spacing=12,
            controls=[header, subheader, question_card, bottom_actions]
        )
    )

    # Inicializa y arranca temporizador
    hydrate()
    page.run_task(countdown)

    return center_wrapper
