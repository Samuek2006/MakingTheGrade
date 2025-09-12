import util.utilidades as util

def menuLogin ():
    while True:
        try:
            print('''
1. Iniciar Sesion
2. Registrate
0. Salir
''')
        except ValueError:
            print("❌ Error: Debes ingresar un número válido.")
        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando menú.")
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando menú.")
            return None
