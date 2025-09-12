import util.utilidades as util
import modules.login as login

def menuLogin ():
    while True:
        try:
            print('''
1. Iniciar Sesion
2. Registrate
0. Salir
''')
            opcion = int(input('Ingresa una Opcion: '))
            match opcion:
                case 1:
                    pass
                case 2:
                    login.register()
                case 0:
                    print('Saliendo...')
                    break
                case _:
                    print('Ingresa una Opcion Valida (0 - 2)')

        except ValueError:
            print("❌ Error: Debes ingresar un número válido.")
        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando menú.")
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando menú.")
            return None
