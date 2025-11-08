# src/modules/login/auth_controller.py
import flet as ft
from ..login.register import RegisterLogic
from ..login.login import LoginLogic
from ..dashboard.dashboardLogic import DashboardLogic
from ...views.dashboard import DashboardUI
 

class AuthController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.show_login()

    def show_login(self, e=None):
        self.page.views.clear()
        # Usar la lógica de login como controlador de la UI
        login_logic = LoginLogic(self.page, router=self)
        self.page.views.append(
            ft.View(route="/login", controls=[login_logic.ui])
        )
        self.page.update()

    def show_register(self, e=None):
        self.page.views.clear()

        # Crear la lógica que a su vez crea su UI
        reg_logic = RegisterLogic(self.page, router=self)

        # Montar la UI que creó RegisterLogic
        self.page.views.append(
            ft.View(route="/register", controls=[reg_logic.ui])
        )
        self.page.update()

    # Navegación que puede llamar RegisterLogic
    def ir_login(self, e=None):
        return self.show_login(e)

    def ir_register(self, e=None):
        return self.show_register(e)

    def show_dashboard(self, user_obj=None):
        self.page.views.clear()
        # Instanciar la logica + dashboard UI
        dash_logic = DashboardLogic(self.page, user=user_obj)
        dash_ui = DashboardUI(self.page, user=user_obj, logic=dash_logic)

        # Crear la vista y adjuntar la barra de navegación al View
        view = ft.View(route="/dashboard", controls=[dash_ui])

        self.page.views.append(view)
        self.page.update()

    def vefCredencialesUser(self, e=None, email=None, password=None):
        try:
            self.page.snack_bar = ft.SnackBar(ft.Text("Probando login..."))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass
