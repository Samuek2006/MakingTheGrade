# views/prueba_panel.py
import flet as ft
from datetime import timedelta
import asyncio
import json
from ast import literal_eval


def build_prueba_panel(page: ft.Page, prueba_id: int) -> ft.Container:
    from ..components.crud import get_prueba_con_preguntas

    data = get_prueba_con_preguntas(prueba_id)
    if not data:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("No se pudo cargar la prueba.", color=ft.Colors.RED),
                    ft.Text(f"ID: {prueba_id}", color=ft.Colors.GREY),
                ],
                spacing=8,
            )
        )

    page.title = f"Prueba #{data['id']} – {data['titulo']}"
    questions = []

    # Normaliza a la estructura que usa tu UI
    for p in data["preguntas"]:
        questions.append(
            {
                "titulo": data["titulo"],
                "enunciado": p.get("enunciado", ""),
                "secuencia": p.get("secuencia", None),
                "opciones": p.get("opciones", []),
                "correcta": p.get("correcta", None),
            }
        )

    if not questions:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(data["titulo"], size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Esta prueba no tiene preguntas registradas.", color=ft.Colors.GREY),
                    ft.ElevatedButton("Volver", on_click=lambda e: _back(page)),
                ],
                spacing=12,
            )
        )

    # -------------------------
    # Estado UI
    # -------------------------
    idx = {"value": 0}
    seleccion = {"value": None}
    total_seconds = data["duracion_seg"] if data["duracion_seg"] else (9 * 60 + 30)
    remaining = {"value": total_seconds}
    stop_timer = {"value": False}

    # Respuestas: { idx: {"seleccion": str, "correcta": bool} }
    user_answers = {}
    # Preguntas ya validadas (para que el 2º click avance)
    validadas = {"set": set()}
    # Aciertos acumulados
    aciertos = {"value": 0}

    progress_bar = ft.ProgressBar(value=0.0, height=6)
    progress_text = ft.Text("", size=12, color=ft.Colors.GREY)
    aciertos_text = ft.Text("", size=12, color=ft.Colors.GREEN)
    timer_icon = ft.Icon(ft.Icons.ALARM, size=16, color=ft.Colors.RED)
    timer_text = ft.Text("", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED)
    subtitle_text = ft.Text("", size=12, color=ft.Colors.GREY)
    title_text = ft.Text(data["titulo"], weight=ft.FontWeight.BOLD, size=16)

    question_rich = ft.Text(spans=[], selectable=False)
    options_col = ft.Column(spacing=12)

    btn_next = None

    # -------------------------
    # Helpers de normalización
    # -------------------------
    def _coerce_to_dict(opt):
        """
        Devuelve un dict {'text': str, 'image': str|None} a partir de:
            - dict original,
            - string JSON,
            - string de repr Python "{'text': '24', 'image': None}",
            - string simple (solo texto).
        """
        if isinstance(opt, dict):
            return {"text": str(opt.get("text", "")).strip(), "image": (opt.get("image") or None)}

        s = str(opt).strip()

        if s.startswith("{") or s.startswith("["):
            try:
                d = json.loads(s.replace("'", '"'))
                if isinstance(d, dict):
                    return {"text": str(d.get("text", "")).strip(), "image": (d.get("image") or None)}
            except Exception:
                # intenta repr de Python
                try:
                    d = literal_eval(s)
                    if isinstance(d, dict):
                        return {"text": str(d.get("text", "")).strip(), "image": (d.get("image") or None)}
                except Exception:
                    pass

        return {"text": s, "image": None}

    def _opt_text(opt) -> str:
        return _coerce_to_dict(opt)["text"]

    def _opt_image(opt):
        return _coerce_to_dict(opt)["image"]

    # -------------------------
    # Helpers UI
    # -------------------------
    def update_timer_label():
        t = str(timedelta(seconds=remaining["value"]))
        mm_ss = t.split(":")[1] + ":" + t.split(":")[2].zfill(2)
        timer_text.value = mm_ss

    def update_aciertos_label():
        total = len(questions)
        aciertos_text.value = f"Aciertos: {aciertos['value']} / {total}"

    def _es_correcta(q, value_text: str) -> bool:
        c = q.get("correcta", None)
        if c is None:
            return False
        if isinstance(c, int):
            try:
                return _opt_text(q.get("opciones", [])[c]) == value_text
            except Exception:
                return False
        return str(c) == value_text

    def _show_feedback(ok: bool):
        msg = "✅ ¡Correcto!" if ok else "❌ Incorrecto"
        color = ft.Colors.GREEN if ok else ft.Colors.RED
        page.snack_bar = ft.SnackBar(ft.Text(msg, color=color, weight=ft.FontWeight.BOLD))
        page.snack_bar.open = True
        page.update()

    def _is_current_validated() -> bool:
        return idx["value"] in validadas["set"]

    # --- NUEVO: helper para repintar solo las opciones actuales ---
    def _refresh_current_options():
        q = questions[idx["value"]]
        options_col.controls = [option_card(o) for o in (q["opciones"] or [])]
        page.update()

    def option_card(opt) -> ft.Container:
        q = questions[idx["value"]]
        data_opt = _coerce_to_dict(opt)
        value_text = data_opt["text"]
        img_url = data_opt["image"]

        selected = (seleccion["value"] == value_text)
        validated = _is_current_validated()

        # Estilos base (seleccionado vs no seleccionado)
        border_color = ft.Colors.BLUE if selected else ft.Colors.GREY_300
        bg = ft.Colors.BLUE_50 if selected else ft.Colors.WHITE
        radio_fill = ft.Colors.BLUE if selected else ft.Colors.GREY_400

        # Si ya se validó esta pregunta, mostramos feedback visual y deshabilitamos clics
        if validated:
            es_ok = _es_correcta(q, value_text)
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
            on_click=(None if validated else (lambda e, t=value_text: select_option(t))),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=content_controls,
            ),
        )

    def _set_btn_next_label():
        if btn_next is not None:
            btn_next.text = "Siguiente" if _is_current_validated() else "Validar"

    def hydrate():
        q = questions[idx["value"]]
        total = len(questions)

        progress_text.value = f"Pregunta {idx['value'] + 1} de {total}"
        progress_bar.value = (idx["value"] + 1) / total

        subtitle_text.value = q["enunciado"]
        spans = [ft.TextSpan(q["enunciado"] + ("\n" if q.get("secuencia") else ""))]
        if q.get("secuencia"):
            spans.append(
                ft.TextSpan(
                    str(q["secuencia"]),
                    style=ft.TextStyle(size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                )
            )
        question_rich.spans = spans

        # Restaurar selección guardada
        seleccion["value"] = user_answers.get(idx["value"], {}).get("seleccion")

        options_col.controls = [option_card(o) for o in (q["opciones"] or [])]
        update_timer_label()
        update_aciertos_label()
        _set_btn_next_label()
        page.update()

    # --- ACTUALIZADO: marca al instante y repinta ---
    def select_option(value_text: str):
        # Si ya está validada, NO permitir cambiar la selección
        if _is_current_validated():
            return

        seleccion["value"] = value_text

        # Si por seguridad estuviera marcada como validada, forzar revalidación
        if idx["value"] in validadas["set"]:
            validadas["set"].discard(idx["value"])

        _set_btn_next_label()
        _refresh_current_options()

    def prev_question(e):
        if idx["value"] > 0:
            idx["value"] -= 1
            hydrate()

    def _validar_actual():
        qindex = idx["value"]
        q = questions[qindex]

        if seleccion["value"] is None:
            page.snack_bar = ft.SnackBar(ft.Text("Responde antes de validar.", color=ft.Colors.RED))
            page.snack_bar.open = True
            page.update()
            return False

        sel_text = seleccion["value"]
        ok = _es_correcta(q, sel_text)
        anterior = user_answers.get(qindex)

        if anterior is None:
            user_answers[qindex] = {"seleccion": sel_text, "correcta": ok}
            if ok:
                aciertos["value"] += 1
        else:
            if ok != bool(anterior.get("correcta")):
                if ok:
                    aciertos["value"] += 1
                else:
                    aciertos["value"] -= 1
            user_answers[qindex]["seleccion"] = sel_text
            user_answers[qindex]["correcta"] = ok

        validadas["set"].add(qindex)
        _show_feedback(ok)
        update_aciertos_label()
        _set_btn_next_label()

        # Refresca la UI para pintar verde/rojo y bloquear clics
        hydrate()
        return True

    def _avanzar_o_finalizar():
        if idx["value"] < len(questions) - 1:
            idx["value"] += 1
            hydrate()
        else:
            finalizar_prueba("finalizado por el usuario")

    def next_question(e):
        if not _is_current_validated():
            if _validar_actual():
                # Botón ahora dirá "Siguiente"; espera segundo clic del usuario
                return
        else:
            _avanzar_o_finalizar()

    def finalizar_prueba(motivo: str = "finalizado"):
        stop_timer["value"] = True
        total = len(questions)
        contestadas = len(user_answers)
        correctas = aciertos["value"]
        pendientes = total - contestadas
        score_pct = 100.0 * correctas / total if total else 0.0

        try:
            from ..components.crud import guardar_respuestas_prueba
            guardar_respuestas_prueba(
                prueba_id=prueba_id,
                total_preguntas=total,
                correctas=correctas,
                respuestas=[
                    {"pregunta_idx": i, "seleccion": d["seleccion"], "correcta": bool(d["correcta"])}
                    for i, d in sorted(user_answers.items(), key=lambda t: t[0])
                ],
                motivo=motivo,
            )
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"No se pudo guardar el intento: {ex}"))
            page.snack_bar.open = True
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Resultado de la prueba"),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(f"Correctas: {correctas}"),
                    ft.Text(f"Incorrectas: {contestadas - correctas}"),
                    ft.Text(f"Sin responder: {pendientes}"),
                    ft.Text(f"Puntaje: {score_pct:.1f}%"),
                    ft.Text(f"Estado: {motivo}"),
                ],
            ),
            actions=[ft.TextButton("Volver al dashboard", on_click=lambda e: _back(page))],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()
        hydrate()

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
            finalizar_prueba("tiempo agotado")

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
        on_click=prev_question,
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
        on_click=next_question,
    )

    # guarda referencia para cambiar el texto dinámicamente
    nonlocal_btn_next = {"ref": None}
    nonlocal_btn_next["ref"] = btn_next

    def set_btn_ref():
        nonlocal btn_next
        btn_next = nonlocal_btn_next["ref"]

    set_btn_ref()

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

    # Inicializa y arranca temporizador
    hydrate()
    page.run_task(countdown)

    return center_wrapper
