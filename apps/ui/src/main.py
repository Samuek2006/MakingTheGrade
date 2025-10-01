import flet as ft
from views.login import LoginAPP

def main(page: ft.Page):
    page.window.width = 390
    page.window.height = 670
    LoginAPP(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
