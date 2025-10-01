import os, time, random

def Limpiar_consola():
    """Limpia la pantalla según el sistema operativo."""
    limpia = os.system("cls" if os.name == "nt" else "clear")
    return limpia

def Stop():
    time.sleep(1)

def Random():
    prueba = random.randint(0, 100)
    return prueba