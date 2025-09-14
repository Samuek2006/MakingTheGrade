import util.corefiles as core
import util.utilidades as util
import util.session as session
from modules.students import studentView as student
from modules.admin import adminView as admin
from modules.qualifiers import qualifierView as qualifier  # <- corrige alias
import getpass, json

DB_User = 'data/user.json'

# Inicializa en PLURAL (coincide con tu DB real)
core.initialize_json(DB_User, {
    "admins": {},
    "qualifiers": {},
    "students": {}
})

def register():
    """
    Registra un estudiante:
    - Pide username y password
    - Llama a admin.studentRegister() para datos personales
    - Guarda en data['students'][identificacion]
    """
    data = core.read_json(DB_User)

    util.Limpiar_consola()
    username = input('Ingresa tu usuario (username): ').strip()

    # Validar duplicados por username o (si existiera) correo
    for section in ["admins", "qualifiers", "students"]:
        for _, info in data.get(section, {}).items():
            if not isinstance(info, dict):
                continue
            cred = info.get("Credenciales", {})
            if cred.get("username") == username or cred.get("correo") == username:
                print("❌ Este usuario ya está registrado, intenta con otro.")
                return

    password = getpass.getpass("Crea una contraseña: ").strip()
    confirm  = getpass.getpass("Confirma tu contraseña: ").strip()
    if password != confirm:
        print("❌ Las contraseñas no coinciden.")
        return

    print('\n=== REGISTRARSE A UN CENTRO DE ESTUDIO ===')
    # Debe devolver al menos {"identificacion": "...", "Nombre": "...", "Apellido": "...", ...}
    student_info = admin.studentRegister()
    identificacion = student_info.get("identificacion")
    if not identificacion:
        print("❌ No se recibió 'identificacion' desde studentRegister().")
        return

    nuevo_student = {
        **student_info,
        "rol": "student",
        "Estado": "Inscrito",
        "Credenciales": {
            "username": username,
            "password": password
            # "correo": correo_opcional  # si luego lo agregas
        }
    }

    data = core.read_json(DB_User)  # refrescar
    data.setdefault("students", {})
    data["students"][identificacion] = nuevo_student
    core.write_json(DB_User, data)

    print(f"✅ Usuario '{username}' registrado con éxito y estudiante creado.")
    util.Stop()
    util.Limpiar_consola()


def login():
    data = core.read_json(DB_User)

    util.Limpiar_consola()
    user_input = input("Ingresa tu usuario (username o correo): ").strip()
    password   = getpass.getpass("Ingresa tu contraseña: ").strip()

    # Recorremos las secciones válidas en PLURAL (coinciden con la DB)
    for section in ["students", "qualifiers", "admins"]:
        usuarios = data.get(section, {})
        if not isinstance(usuarios, dict):
            continue

        for user_id, info in usuarios.items():
            if not isinstance(info, dict):
                continue

            cred = info.get("Credenciales", {})
            # Acepta login por 'username' o 'correo'
            if user_input == cred.get("username") or user_input == cred.get("correo"):
                if password == cred.get("password"):
                    # Rol: tomamos el guardado o inferimos por sección
                    rol = (info.get("rol") or section[:-1]).strip().lower()  # students->student, qualifiers->qualifier, admins->admin

                    # Guardar sesión
                    session.session["is_logged_in"] = True
                    session.session["user_id"] = user_id
                    session.session["username"] = cred.get("username") or user_input
                    session.session["rol"] = rol

                    print(f"✅ Bienvenido {info.get('Nombre', 'Usuario')} (Rol: {rol})")

                    # 👉 Mantener IF por rol (como pediste)
                    if rol == "student":
                        util.Limpiar_consola()
                        student.menuStudent()
                    elif rol == "qualifier":
                        util.Limpiar_consola()
                        qualifier.menuQualifier()
                    elif rol == "admin":
                        util.Limpiar_consola()
                        admin.menuAdmin()
                    else:
                        util.Limpiar_consola()
                        print(f"⚠️ Rol desconocido: {rol}")

                    return True
                else:
                    print("❌ Contraseña incorrecta.")
                    return False

    print("❌ Usuario no encontrado.")
    return False
