import util.corefiles as corefiles

DB_Users = 'data/user.json'
corefiles.initialize_json(DB_Users, {
    "admins" : {},
    "qualifiers" : {},
    "students" : {}
})

def menuAdmin():
    pass

def addStudent():
    identificacion = input('Ingresa el Documento de Identidad del Estudiante: ').strip()
    rol = 'student'
    name = input('Ingresa el Nombre del Estudiante: ')
    apellido = input('Ingresa el Apellido del Estudiante: ')
    direccion = input('Ingresa la Direccion de Residencia del Estudiante: ')
    telefono = int(input('Ingresa el Telefono del Estudiante: '))

    student = {
        "identificacion": identificacion,
        "Nombre": name,
        "Apellido": apellido,
        "Direccion": direccion,
        "telefono": telefono,
        "rol": rol,
        "Estado": "Inscrito",
        "Credenciales": {}
    }

    corefiles.update_json(DB_Users, {identificacion: student}, ["students"])

    print(f'✅ Student {name} {apellido} creado correctamente')
    return student

def addQualifier():
    identificacion = input('Ingresa el Documento de Identidad del Calificador: ').strip()
    rol = 'qualifier'
    name = input('Ingresa el Nombre del Calificador: ')
    apellido = input('Ingresa el Apellido del Calificador: ')
    telefono = int(input('Ingresa el Telefono del Calificador: '))

    qualifier = {
        "identificacion": identificacion,
        "Nombre": name,
        "Apellido": apellido,
        "telefono": telefono,
        "rol": rol,
        "Estado": "Inscrito",
        "Credenciales": {}
    }

    corefiles.update_json(DB_Users, {identificacion: qualifier}, ["qualifiers"])

    print(f'✅ Calificador {name} {apellido} creado correctamente')
    return qualifier

def addAdmin():
    identificacion = input('Ingresa el Documento de Identidad del Admin: ').strip()
    rol = 'admin'
    name = input('Ingresa el Nombre del Admin: ')
    apellido = input('Ingresa el Apellido del Admin: ')
    telefono = int(input('Ingresa el Telefono del Admin: '))

    admin = {
        "identificacion": identificacion,
        "Nombre": name,
        "Apellido": apellido,
        "telefono": telefono,
        "rol": rol,
        "Estado": "Inscrito",
        "Credenciales": {}
    }

    corefiles.update_json(DB_Users, {identificacion: admin}, ["admins"])

    print(f'✅ Admin {name} {apellido} creado correctamente')
    return admin