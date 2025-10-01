import flet as ft

# Utilidad para elegir ícono según plataforma
def _adaptive_icon(page: ft.Page, ios_icon, android_icon):
    return ios_icon if page.platform in (ft.PagePlatform.IOS, ft.PagePlatform.MACOS) else android_icon

def build_navigation_bar(
        page: ft.Page,
        selected_index: int = 0,
        on_change=None,
    ) -> ft.NavigationBar:

    return ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=_adaptive_icon(page, ft.CupertinoIcons.HOME, ft.Icons.HOME),
                label="Inicio",
            ),
            ft.NavigationBarDestination(
                icon=_adaptive_icon(page, ft.CupertinoIcons.CHART_BAR, ft.Icons.BAR_CHART),
                label="Resultados",
            ),
            ft.NavigationBarDestination(
                icon=_adaptive_icon(page, ft.CupertinoIcons.PERSON_3_FILL, ft.Icons.PERSON),
                label="Perfil",
            ),
        ],
    )
