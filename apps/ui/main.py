import os
import sys
from pathlib import Path

# Configurar PYTHONPYCACHEPREFIX para centralizar todos los .pyc en una carpeta global
# Esto debe hacerse ANTES de cualquier otro import
# Requiere Python 3.8+
if sys.version_info >= (3, 8):
    _cache_dir = Path(__file__).parent / ".pycache"
    _cache_dir.mkdir(exist_ok=True)
    _cache_path = str(_cache_dir.absolute())

    # Establecer sys.pycache_prefix (método programático recomendado)
    # Esto fuerza a Python a usar esta ubicación para TODOS los .pyc
    sys.pycache_prefix = _cache_path

    # También establecer la variable de entorno por si acaso
    os.environ["PYTHONPYCACHEPREFIX"] = _cache_path

    # Verificar que se aplicó correctamente
    if hasattr(sys, 'pycache_prefix') and sys.pycache_prefix:
        # La configuración está activa
        pass

import flet as ft
import asyncio

from src.views.splash import SplashUI
from src.modules.login.auth_controller import AuthController


def main(page: ft.Page):
    # Usar dimensiones del dispositivo; evitar tamaños fijos
    page.window.full_screen = True
    page.window.title_bar_hidden = False
    page.window.title_bar_buttons_hidden = True
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
