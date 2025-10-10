import flet as ft
from src.views.login import LoginAPP

# Fuerza inclusión de certifi en el bundle y asegura ruta de certificados en runtime 
try:
    import os
    import certifi  # noqa: F401  (referencia explícita para empaquetado)
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except Exception:
    pass
try:
    # Inicializa la base local (SQLite) en el arranque.
    from db.db import init_db
    init_db(create_all=True)
except Exception as _e:
    # No detenemos la app si la inicialización falla; la UI seguirá cargando.
    # Puedes revisar logs si necesitas depurar la base de datos.
    pass

def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 670
    LoginAPP(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
