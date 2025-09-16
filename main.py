import modules.mainMenu as menu
import modules.qualifiers.qualifierView as qualifier
import json

def main():
    while True:
        try:
            menu.menuLogin()
            return menu

        except ValueError:
            print("❌ Error: Ingresa un valor válido.")

        except FileNotFoundError:
            print("❌ Error: No se encontró la base de datos (user.json).")
            break

        except json.JSONDecodeError:
            print("❌ Error: El archivo de base de datos está dañado o mal formado.")
            break

        except KeyError as e:
            print(f"❌ Error: Falta la clave {e} en los datos del sistema.")

        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando menú principal.")
            break

        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando menú principal.")
            break

        except Exception as e:
            print(f"⚠️ Error inesperado: {e}")
            break

if __name__ == '__main__':
    main()

