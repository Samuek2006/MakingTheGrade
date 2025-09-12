import util.corefiles as core
import util.utilidades as util
import util.session as session
from modules.students import studentView as student
from modules.admin import adminView as admin
from modules.qualifiers import qualifierView as quialifier
import getpass, json

DB_User = 'data/user.json'
core.initialize_json(DB_User, {
    "admin" : {},
    "qualifier" : {},
    "students" : {}
})

def register():
    data = core.read_json(DB_User)

    user = input('Ingresa  tu correo: ').strip()
    rol = 'student'

    # Validar que no exista ya el correo en ninguna sección
    for section in ["admin", "qualifier", "students"]:
        for _, info in data.get(section, {}).items():
            if isinstance(info, dict) and info.get("Credenciales", {}).get("correo")== user:
                print("❌ Este correo ya está registrado, intenta con otro.")
                return

    password = getpass.getpass("Crea una contraseña: ")
    confirm = getpass.getpass("Confirma tu contraseña: ")

    if password != confirm:
        print("❌ Las contraseñas no coinciden.")
        return

    # Pedir datos del camper desde vistaCamper
    print("\n📝 Ahora ingresa los datos personales del camper:")

    print('=== REGISTRARSE A CAMPUSLANDS ===')
    student = admin.studentRegister()
    identificacion = student["identificacion"]

    data_campus = core.read_json(DB_User)
    data_campus["students"][identificacion]["Credenciales"] = {
        "correo": user,
        "password": password
    }
    core.write_json(DB_User, data_campus)
    print(f"✅ Usuario {user} registrado con éxito y camper creado.")

    util.Stop()
    util.Limpiar_consola()

def login():
    data = core.read_json(DB_User)

    user = input("Ingresa tu correo: ").strip()
    password = getpass.getpass("Ingresa tu contraseña: ")

    # Buscar en campers, trainers, admins
    for section in ["camperCampusLands", "trainerCampusLands", "adminCampusLands"]:
        for user_id, info in data.get(section, {}).items():
            if not isinstance(info, dict):
                continue  # seguridad, si se cuela algo que no sea dict

            cred = info.get("Credenciales", {})
            if cred.get("correo") == user:
                if cred.get("password") == password:
                    # Normalizamos el rol (en mayúscula inicial)
                    rol = (info.get("Rol") or info.get("rol") or "").capitalize()

                    if not rol:
                        print("⚠️ El usuario no tiene un rol asignado en la base de datos.")
                        return False

                    # Guardamos la sesión
                    session.session["is_logged_in"] = True
                    session.session["user_id"] = user_id
                    session.session["correo"] = user
                    session.session["rol"] = rol

                    print(f"✅ Bienvenido {info.get('Nombre', 'Usuario')} (Rol: {rol})")

                    # Redirigir según rol
                    if rol == "students":
                        student.menuStudent()

                    elif rol == "qualifier":
                        quialifier.menuQualifier()

                    elif rol == "admin":
                        admin.menuAdmin()

                    else:
                        print(f"⚠️ Rol desconocido: {rol}")

                    return True
                else:
                    print("❌ Contraseña incorrecta.")
                    return False
