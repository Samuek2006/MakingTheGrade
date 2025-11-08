# src/views/dashboard.py
from __future__ import annotations
import flet as ft
from typing import List, Dict, Any, Optional


class DashboardUI(ft.Column):
    def __init__(self, page: ft.Page, user: Optional[dict] = None, logic: Optional[object] = None):
        super().__init__(spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page = page
        self.user = user or {}
        self.logic = logic

        self.page.adaptive = True
        self.page.title = "Home"

        # ======== Contenido principal ========
        header = ft.Text("Pruebas disponibles", size=22, weight=ft.FontWeight.BOLD)

        # factory de tarjeta
        def card(titulo: str, subtitulo: str | None, bg, on_click):
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.QUIZ, color=ft.Colors.BLUE, size=32),
                        ft.Column(
                            [
                                ft.Text(titulo, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(subtitulo or "", size=12, color=ft.Colors.GREY),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(name=ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY, size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=15,
                ),
                bgcolor=bg,
                border_radius=10,
                padding=15,
                ink=True,
                on_click=on_click,
                width=500,
            )

        # Construye la lista de tarjetas desde la data
        def build_cards(pruebas: List[Dict[str, Any]] | None):
            items: List[ft.Control] = []
            if not pruebas:
                # Estado vacío
                items.append(
                    ft.Container(
                        padding=20,
                        border_radius=12,
                        bgcolor=ft.Colors.GREY_100,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Aún no hay pruebas disponibles",
                                    weight=ft.FontWeight.BOLD,
                                    size=14,
                                )
                            ],
                            spacing=6,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )
                return items

            for p in pruebas:
                items.append(
                    card(
                        titulo=p.get("titulo", "Prueba"),
                        subtitulo=p.get("descripcion", ""),
                        bg=ft.Colors.WHITE,
                        on_click=lambda e, pid=p.get("id"): print(f"[DASH] Abrir prueba {pid}"),
                    )
                )
            return items

        # Intentar traer pruebas si hay lógica; si no, mostrar vacío
        pruebas = None
        if self.logic and hasattr(self.logic, "cargaPruebas"):
            try:
                pruebas = self.logic.cargaPruebas()
            except Exception:
                pruebas = None

        body = ft.Column(
            controls=[header, *build_cards(pruebas)],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.controls = [
            ft.Container(expand=True, alignment=ft.alignment.top_center, content=body)
        ]

        self.page.update()
