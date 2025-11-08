import flet as ft

class ButtonLogin(ft.ElevatedButton):
    def __init__(self, text, on_click=None):
        super().__init__(
            text=text,
            bgcolor=ft.Colors.ORANGE_300,
            color=ft.Colors.GREEN_800,
            on_click=on_click,
        )