from modules.qualifiers import qualifierView as quialifier
import util.corefiles as corefiles
import util.utilidades as util
import json

DB_Prueba   = 'data/evidence.json'
DB_Qualifer = "data/grades.json"

DB_Users = 'data/user.json'
corefiles.initialize_json(DB_Users, {
    "admins" : {},
    "qualifiers" : {},
    "students" : {}
})

def menuAdmin():
    while True:
        try:
            print("""
===== MENÚ ADMIN =====
1. Reportes
2. Agregar Student
3. Agregar Qualifier
4. Agregar Admin
0. Salir
""")

            opcion = int(input('Ingresa una Opcion: '))
            match opcion:
                case 1:
                    util.Limpiar_consola()
                    reportes()
                    util.Stop()
                    util.Limpiar_consola()

                case 2:
                    util.Limpiar_consola()
                    addStudent()
                    util.Stop()
                    util.Limpiar_consola()

                case 3:
                    util.Limpiar_consola()
                    addQualifier()
                    util.Stop()
                    util.Limpiar_consola()

                case 4:
                    util.Limpiar_consola()
                    addAdmin()
                    util.Stop()
                    util.Limpiar_consola()

                case 0:
                    util.Limpiar_consola()
                    print('Saliendo del Sistema...')
                    util.Stop()
                    util.Limpiar_consola()
                    break

                case _:
                    print("⚠️ Opción no válida.")
                    util.Stop()

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

def reportes():
        try:
            with open(DB_Qualifer, 'r', encoding='utf-8') as f:
                grades = json.load(f)
        except Exception as e:
            print("No se pudo leer 'data/grades.json':", e)
            return

        try:
                with open(DB_Prueba, 'r', encoding='utf-8') as f:
                    evidence = json.load(f)
        except Exception as e:
                print("No se pudo leer 'data/evidence.json':", e)
                evidence = {}

        resultados = grades.get('Resultados', {})

        # Mapas de preguntas y puntos
        cerradas = evidence.get('PreguntasCerradas', [])
        cerradas_map = {q['id']: {'correct': q.get('correct'), 'points': q.get('points', 0)} for q in cerradas}
        total_cerradas_points = sum(q.get('points', 0) for q in cerradas)

        cortas = evidence.get('PreguntasCortas', [])
        total_cortas_points = sum(q.get('max_points', 0) for q in cortas)

        ensayos = evidence.get('Ensayo', [])
        total_ensayo_points = sum(q.get('max_points', 0) for q in ensayos)

        estudiantes = set()
        for t in ('Cerradas', 'Cortas', 'Ensayo'):
            estudiantes.update(resultados.get(t, {}).keys())

        print("\n===== REPORTE DE ESTUDIANTES =====\n")
        if not estudiantes:
            print("⚠️ No hay estudiantes con registro de pruebas.")
            return

        for estudiante in sorted(estudiantes):
            print(f"Estudiante: {estudiante}")
            total_obtenido = 0.0
            total_posible = 0.0

            # Cerradas: automática
            cerradas_entry = resultados.get('Cerradas', {}).get(estudiante)
            if cerradas_entry:
                answers = cerradas_entry.get('answers', {})
                score = 0.0
                possible = 0.0
                for qid, resp in answers.items():
                    meta = cerradas_map.get(qid)
                    if meta:
                        pts = meta.get('points', 0)
                        possible += pts
                        if resp == meta.get('correct'):
                            score += pts
                print(f"  Cerradas: {score}/{possible} puntos")
                total_obtenido += score
                total_posible += possible
            else:
                if total_cerradas_points > 0:
                    print("  Cerradas: (sin intento)")

            # Cortas: si hay grade lo muestra, sino pendiente
            cortas_entry = resultados.get('Cortas', {}).get(estudiante)
            if cortas_entry:
                grade = cortas_entry.get('grade')
                if grade is not None:
                    print(f"  Cortas: {grade}/{total_cortas_points} puntos")
                    total_obtenido += float(grade)
                    total_posible += total_cortas_points
                else:
                    answered = len(cortas_entry.get('answers', {}))
                    print(f"  Cortas: Pendiente de calificar (respondió {answered} preguntas)")
            else:
                if total_cortas_points > 0:
                    print("  Cortas: (sin intento)")

            # Ensayo: si hay grade (puede ser %), lo convierte a puntos si hay max_points definidos
            ensayo_entry = resultados.get('Ensayo', {}).get(estudiante)
            if ensayo_entry:
                grade = ensayo_entry.get('grade')
                if grade is not None:
                    if total_ensayo_points > 0 and float(grade) <= 100:
                        obtained = (float(grade) / 100.0) * total_ensayo_points
                        print(f"  Ensayo: {grade}% → {obtained}/{total_ensayo_points} puntos")
                        total_obtenido += obtained
                        total_posible += total_ensayo_points
                    else:
                        print(f"  Ensayo: {grade} puntos de {total_ensayo_points}")
                        total_obtenido += float(grade)
                        total_posible += total_ensayo_points
                else:
                    print("  Ensayo: Pendiente de calificar")
            else:
                if total_ensayo_points > 0:
                    print("  Ensayo: (sin intento)")

            # Consolidado
            if total_posible > 0:
                pct = (total_obtenido / total_posible) * 100
                print(f"  → Total: {total_obtenido:.2f}/{total_posible:.2f} puntos ({pct:.1f}%)\n")
            else:
                print("\n")