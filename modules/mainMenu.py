import util.utilidades as util
import modules.login as login

def menuLogin ():
    while True:
        try:
            util.Limpiar_consola()
            print('''
1. Iniciar Sesion
2. Registrate
0. Salir
''')
            opcion = int(input('Ingresa una Opcion: '))
            match opcion:
                case 1:
                    login.login()
                    util.Stop()
                    util.Limpiar_consola()
                case 2:
                    login.register()
                    util.Stop()
                    util.Limpiar_consola()
                case 0:
                    print('Saliendo...')
                    util.Stop()
                    util.Limpiar_consola()
                    break
                case _:
                    print('Ingresa una Opcion Valida (0 - 2)')
                    util.Stop()
                    util.Limpiar_consola()

        except ValueError:
            print("❌ Error: Debes ingresar un número válido.")
            util.Stop()
        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando menú.")
            util.Stop()
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando menú.")
            util.Stop()
            return None
