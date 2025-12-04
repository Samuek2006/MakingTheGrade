import flet as ft

class ButtonLogin(ft.ElevatedButton):
    def __init__(self, text, on_click=None):
        C = getattr(ft, "colors", None) or getattr(ft, "Colors", None)
        PRIMARY = getattr(C, "BLUE_700", getattr(C, "BLUE", None))
        PRIMARY_LIGHT = getattr(C, "BLUE_600", getattr(C, "BLUE", None))
        
        super().__init__(
            text=text,
            icon=ft.Icons.LOGIN_ROUNDED,
            bgcolor=PRIMARY,
            color=getattr(C, "WHITE", None),
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY},
                color={ft.ControlState.DEFAULT: getattr(C, "WHITE", None)},
                overlay_color={ft.ControlState.HOVERED: PRIMARY_LIGHT},
                padding=ft.padding.symmetric(18, 0),
                shape=ft.RoundedRectangleBorder(radius=16),
                elevation={ft.ControlState.DEFAULT: 4, ft.ControlState.HOVERED: 8},
                animation_duration=200,
            ),
        )