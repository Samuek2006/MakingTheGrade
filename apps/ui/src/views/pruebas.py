import flet as ft
from apps.ui.src.views.nav_bar import build_navigation_bar
from apps.ui.src.views.prueba_panel import build_prueba_panel

class PruebasApp:
    def __init__(self, page: ft.Page):
        page.adaptive = True
        page.title = "Pruebas Lógica"
        page.padding = 12
        page.bgcolor = ft.Colors.GREY_100

        def handle_nav_change(e: ft.ControlEvent):
            print("Tab seleccionado:", e.control.selected_index)

        page.navigation_bar = build_navigation_bar(
            page=page,
            selected_index=0,
            on_change=handle_nav_change
        )

        panel = build_prueba_panel(page)  # <--- usa la función
        page.add(panel)
        page.update()
