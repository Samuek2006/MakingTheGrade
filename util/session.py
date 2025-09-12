session = {
    "is_logged_in": False,
    "user": None,
    "rol": None
}

def cerrar_sesion():
    session_default = '''session = {
    "is_logged_in": False,
    "user": None,
    "rol": None
}'''
    with open(__file__, "w", encoding="utf-8") as f:
        f.write(session_default)