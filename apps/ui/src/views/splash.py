import flet as ft

YELLOW = "#FCE44D"
INK = "#0F172A"
INK_2 = "#1E293B"


class SplashUI(ft.Container):
    def __init__(self, page: ft.Page, on_ready=None):
        super().__init__(
            expand=True,
            gradient=ft.RadialGradient(
                center=ft.alignment.center,
                radius=1.2,
                colors=[INK, INK_2],
                stops=[0.2, 1.0],
            ),
            alignment=ft.alignment.center,
        )

        self.page = page
        self.on_ready = on_ready

        # Logo con "respiración"
        self.logo = ft.Container(
            content=ft.Icon(ft.Icons.SCHOOL, size=86, color=YELLOW),
            scale=1.0,
            animate_scale=ft.Animation(700, ft.AnimationCurve.EASE_IN_OUT),
        )

        # Título con aparición suave
        self.title = ft.Text(
            "Marking The Grade",
            size=30,
            weight=ft.FontWeight.W_900,
            color=YELLOW,
            opacity=0.0,
            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
        )

        # Subtítulo
        self.subtitle = ft.Text("Cargando", size=14, color="#e5e7eb", opacity=0.9)

        # Puntos animados
        def dot():
            return ft.Container(
                width=8,
                height=8,
                bgcolor=YELLOW,
                border_radius=8,
                opacity=0.2,
                animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            )

        self.dots = [dot(), dot(), dot()]

        # Indicador giratorio
        self.ring = ft.ProgressRing(width=42, height=42, stroke_width=5, color=YELLOW)

        # Tarjeta central
        card = ft.Container(
            bgcolor="transparent",
            content=ft.Column(
                [
                    self.logo,
                    self.title,
                    ft.Container(height=4),
                    self.ring,
                    ft.Container(height=12),
                    ft.Row(
                        [self.subtitle, ft.Container(width=6), ft.Row(self.dots, spacing=6)],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            alignment=ft.alignment.center,
        )

        backdrop = ft.Stack(
            [
                ft.Container(left=-60, top=-60, width=200, height=200, border_radius=300, bgcolor="#fce44d22"),
                ft.Container(right=-50, bottom=-50, width=160, height=160, border_radius=300, bgcolor="#fce44d18"),
                card,
            ],
            expand=True,
        )

        self.content = ft.Container(expand=True, content=backdrop, alignment=ft.alignment.center)

        # Timers
        self._grow = True
        self._tick = 0
        self._timer_breath = None
        self._timer_dots = None

        # No iniciar animaciones aún; esperar a que el control esté montado

    def did_mount(self):
        # Se llama cuando el control ya está agregado a la página/árbol
        try:
            self._attach_timers()
        except Exception:
            pass
        self._show()

    def _attach_timers(self):
        try:
            self._timer_breath = ft.Timer(interval=700, repeat=True, on_tick=self._breath)
            self._timer_dots = ft.Timer(interval=350, repeat=True, on_tick=self._pulse_dots)
            # Los timers deben estar en el árbol de controles para funcionar
            self.page.overlay.append(self._timer_breath)
            self.page.overlay.append(self._timer_dots)
            self.page.update()
        except Exception:
            pass

    # Animaciones
    def _show(self):
        self.title.opacity = 1.0
        self.update()

    def _breath(self, _):
        self.logo.scale = 1.12 if self._grow else 1.0
        self._grow = not self._grow
        self.update()

    def _pulse_dots(self, _):
        active = self._tick % 3
        for i, d in enumerate(self.dots):
            d.opacity = 1.0 if i == active else (0.5 if (i + 1) % 3 == active else 0.2)
        self._tick += 1
        self.update()

    def will_unmount(self):
        try:
            if self._timer_breath:
                self._timer_breath.cancel()
            if self._timer_dots:
                self._timer_dots.cancel()
            if hasattr(self.page, "overlay"):
                try:
                    if self._timer_breath in self.page.overlay:
                        self.page.overlay.remove(self._timer_breath)
                    if self._timer_dots in self.page.overlay:
                        self.page.overlay.remove(self._timer_dots)
                except Exception:
                    pass
        except Exception:
            pass
