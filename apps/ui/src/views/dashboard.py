import flet as ft

class Dashboard:
    def __init__(self, page: ft.Page):
        page.adaptive = True
        page.title = "Home"

        # Imports locales para evitar circulares
        try:
            from .nav_bar import build_navigation_bar
        except Exception as ex:
            print("[DASH] Error importando nav_bar:", ex)
            page.add(ft.Text(f"Error importando nav_bar: {ex}", color=ft.Colors.RED)); page.update(); return

        try:
            from .prueba_panel import build_prueba_panel
        except Exception as ex:
            print("[DASH] Error importando prueba_panel:", ex)
            page.add(ft.Text(f"Error importando prueba_panel: {ex}", color=ft.Colors.RED)); page.update(); return

        # CRUD de pruebas
        try:
            from ..components.crud import get_pruebas_activas
        except Exception as ex:
            print("[DASH] Error importando crud_pruebas:", ex)
            page.add(ft.Text(f"Error importando crud_pruebas: {ex}", color=ft.Colors.RED)); page.update(); return

        def handle_nav_change(e: ft.ControlEvent):
            idx = e.control.selected_index
            print("[DASH] Tab seleccionado:", idx)

        # Navigation bar
        try:
            page.navigation_bar = build_navigation_bar(page=page, selected_index=0, on_change=handle_nav_change)
        except Exception as ex:
            print("[DASH] Error construyendo navigation_bar:", ex)
            page.add(ft.Text(f"Error construyendo navigation_bar: {ex}", color=ft.Colors.RED)); page.update(); return

        header = ft.Text("Pruebas disponibles", size=22, weight=ft.FontWeight.BOLD)

        def card(titulo, subtitulo, bg, on_click):
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.QUIZ, color=ft.Colors.BLUE, size=32),
                        ft.Column(
                            [ft.Text(titulo, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(subtitulo or "", size=12, color=ft.Colors.GREY)],
                            alignment=ft.MainAxisAlignment.CENTER, spacing=2, expand=True,
                        ),
                        ft.Icon(name=ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY, size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15,
                ),
                bgcolor=bg, border_radius=10, padding=15, ink=True,
                on_click=on_click, width=500,
            )

        # Cargar pruebas desde BD
        pruebas = get_pruebas_activas(limit=100)
        print(f"[DASH] Pruebas encontradas: {len(pruebas)}")

        items = [header]

        if not pruebas:
            items.append(ft.Text("No hay pruebas disponibles.", color=ft.Colors.GREY))
        else:
            # Genera una card por prueba
            for i, p in enumerate(pruebas):
                # Alterna color de fondo para darle ritmo
                bg = ft.Colors.WHITE if i % 2 == 0 else ft.Colors.GREY_200

                def go_to_prueba(e, prueba_id=p["id"]):
                    try:
                        page.clean()
                        # Si tu panel necesita el ID de la prueba:
                        # build_prueba_panel(page, prueba_id=prueba_id)
                        page.add(build_prueba_panel(page, prueba_id=prueba_id))
                        page.update()
                    except Exception as ex:
                        print("[DASH] Error abriendo Prueba:", prueba_id, ex)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error abriendo la prueba {prueba_id}: {ex}"))
                        page.snack_bar.open = True
                        page.update()

                items.append(card(
                    titulo=p["titulo"],
                    subtitulo=p.get("subtitulo", ""),
                    bg=bg,
                    on_click=go_to_prueba
                ))

        page.add(*items)
        page.update()
