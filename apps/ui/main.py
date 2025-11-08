import flet as ft
import asyncio

from src.views.splash import SplashUI
from src.modules.login.auth_controller import AuthController


def main(page: ft.Page):
    # Usar dimensiones del dispositivo; evitar tamaños fijos
    page.window.full_screen = False
    page.window.title_bar_hidden = False
    page.window.title_bar_buttons_hidden = False
    page.padding = 0

    # Mostrar el Splash desde su componente
    page.views.clear()
    splash = SplashUI(page)
    page.views.append(ft.View(route="/splash", controls=[splash]))
    page.update()

    # Mostrar el login justo después del splash sin esperas extra
    async def go_login():
        await asyncio.sleep(1.0)  # duración total visible del splash

        def mount():
            page.views.clear()
            AuthController(page)

        if hasattr(page, "run_on_idle"):
            page.run_on_idle(mount)
        else:
            mount()

    try:
        page.run_task(go_login)
    except AssertionError:
        # compatibilidad con firmas antiguas
        page.run_task(go_login())


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
