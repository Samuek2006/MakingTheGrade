import json
from datetime import datetime

import util.corefiles as corefiles
import util.utilidades as utilidades

# === BDs ===
DB_Prueba   = 'data/evidence.json'
DB_Qualifer = 'data/grades.json'

# === Inicialización (misma estructura, sin POO) ===
corefiles.initialize_json(DB_Prueba, {
    "PreguntasCerradas": [],
    "PreguntasCortas":  [],
    "PreguntasEnsayo":  []
})

corefiles.initialize_json(DB_Qualifer, {
    "Resultados": {          # respuestas/resultado del alumno
        "Cerradas": {},
        "Cortas":   {},
        "Ensayo":   {}
    },
    "Qualifer_ensayos": {    # calificación del corrector
        "Cortas": {},
        "Ensayo": {}
    }
})

# ==============================
#  MENÚ CALIFICACIÓN (sin OOP)
# ==============================
def menuQualifier():
    while True:
        print("\n===== MENÚ CALIFICACIÓN =====")
        print("1. Listar pendientes (Cortas)")
        print("2. Listar pendientes (Ensayo)")
        print("3. Calificar pendiente")
        print("0. Salir")
        opcion = input("👉 Opción: ").strip()

        match opcion:
            case '1':
                utilidades.Limpiar_consola()
                listar_pendientes("Cortas")
                utilidades.Limpiar_consola()

            case '2':
                utilidades.Limpiar_consola()
                listar_pendientes("Ensayo")
                utilidades.Limpiar_consola()

            case '3':
                utilidades.Limpiar_consola()
                tipo = input("Tipo (Cortas/Ensayo): ").strip().title()
                if tipo not in ("Cortas", "Ensayo"):
                    print("❌ Tipo inválido.")
                    continue
                pendientes = listar_pendientes(tipo)
                if not pendientes:
                    continue
                try:
                    idx  = int(input("Número del pendiente a calificar: ").strip())
                except ValueError:
                    print("❌ Entrada inválida.")
                    continue
                calificar_pendiente(tipo, idx)
                utilidades.Limpiar_consola()

            case '0':
                utilidades.Limpiar_consola()
                print("\n👋 Saliendo. ¡Hasta luego!")
                break

            case _:
                utilidades.Limpiar_consola()
                print("❌ Opción inválida.")
                utilidades.Limpiar_consola()

# ==============================
#  LISTAR Y CALIFICAR PENDIENTES
# ==============================
def listar_pendientes(tipo: str):
    data = corefiles.read_json(DB_Qualifer) or {}
    data.setdefault("Resultados", {"Cerradas": {}, "Cortas": {}, "Ensayo": {}})
    data.setdefault("Qualifer_ensayos", {"Cortas": {}, "Ensayo": {}})

    resultados = data["Resultados"].get(tipo, {}) or {}
    ya_calificados = data["Qualifer_ensayos"].get(tipo, {}) or {}

    pendientes = []
    for ident, payload in resultados.items():
        graded_flag = bool(payload.get("graded")) or (ident in ya_calificados) or ("grade" in payload)
        if not graded_flag:
            pendientes.append((ident, payload))

    if not pendientes:
        print(f"\n✅ No hay pendientes en {tipo}.")
        utilidades.Stop()
        utilidades.Limpiar_consola()
        return []

    print(f"\n📌 Pendientes en {tipo}:")
    for i, (ident, payload) in enumerate(pendientes, start=1):
        when = payload.get("datetime", "-")
        answers = payload.get("answers") or {}
        print(f"{i}. [{ident}] {when} | respuestas: {len(answers)}")
    input('Enter para continuar...')
    return pendientes

def calificar_pendiente(tipo: str, indice: int):
    # Lee grades.json
    data_grades = corefiles.read_json(DB_Qualifer) or {}
    data_grades.setdefault("Resultados", {"Cerradas": {}, "Cortas": {}, "Ensayo": {}})
    data_grades.setdefault("Qualifer_ensayos", {"Cortas": {}, "Ensayo": {}})

    resultados = data_grades["Resultados"].get(tipo, {}) or {}
    ya_calificados = data_grades["Qualifer_ensayos"].get(tipo, {}) or {}

    # Construye lista de pendientes (ident, payload) sin helpers
    pendientes = []
    for ident, payload in resultados.items():
        graded_flag = bool(payload.get("graded")) or (ident in ya_calificados) or ("grade" in payload)
        if not graded_flag:
            pendientes.append((ident, payload))

    if not pendientes:
        print("⚠️ No hay elementos por calificar.")
        utilidades.Stop()
        utilidades.Limpiar_consola()
        return False
    if indice < 1 or indice > len(pendientes):
        print("❌ Índice inválido.")
        return False

    ident, payload = pendientes[indice - 1]
    answers = payload.get("answers") or {}
    total_q = payload.get("total_questions", len(answers))

    # Lee banco de preguntas directamente de evidence.json
    data_prueba = corefiles.read_json(DB_Prueba) or {}
    if tipo == "Cortas":
        lista_preg = data_prueba.get("PreguntasCortas", [])
        pref = "PC"
    else:
        lista_preg = data_prueba.get("PreguntasEnsayo", [])
        pref = "PE"

    # Mapa id -> texto de pregunta (sin helpers ni POO)
    mapa_texto = {}
    for i, q in enumerate(lista_preg, start=1):
        qid = q.get("id", f"{pref}{i}")
        mapa_texto[qid] = q.get("text", f"(Sin texto para {qid})")

    # Calificación por pregunta
    print(f"\n📝 Calificando [{tipo}] de [{ident}] — {len(answers)} respuesta(s)")
    calificaciones_pregunta = {}
    suma = 0.0
    cuenta = 0

    # Recorre en orden por id de pregunta
    for qid in sorted(answers.keys()):
        texto = mapa_texto.get(qid, f"(No existe en banco) {qid}")
        resp  = answers[qid]

        utilidades.Limpiar_consola()
        print("────────────────────────────────────────")
        print(f"Pregunta: {qid}")
        print(f"Texto   : {texto}")
        print(f"Respuesta del alumno:\n{resp}\n")
        while True:
            try:
                nota = float(input("Asigna nota a esta pregunta (0-100): ").strip())
                if 0.0 <= nota <= 100.0:
                    break
                else:
                    print("❌ Ingresa un valor entre 0 y 100.")
                    utilidades.Stop()
                    utilidades.Limpiar_consola()
            except ValueError:
                print("❌ Número inválido. Intenta de nuevo.")
                utilidades.Stop()
                utilidades.Limpiar_consola()

        calificaciones_pregunta[qid] = nota
        suma += nota
        cuenta += 1

    # Promedio final (si no hubo respuestas, 0)
    grade_total = round((suma / cuenta), 2) if cuenta else 0.0

    # Guarda calificación del corrector bajo Qualifer_ensayos.<tipo>.<ident>
    now = datetime.now().isoformat(timespec="seconds")
    obj_calif = {
        "grade_total": grade_total,
        "graded_at": now,
        "per_question_grades": calificaciones_pregunta,
        "answers": answers,
        "total_questions": total_q
    }
    corefiles.update_json(DB_Qualifer, {ident: obj_calif}, ["Qualifer_ensayos", tipo])

    # Marca en Resultados como calificado y copia la nota total
    corefiles.update_json(DB_Qualifer, {"graded": True, "grade": grade_total}, ["Resultados", tipo, ident])

    print(f"\n✅ Calificado [{tipo}] -> {ident}")
    print(f"   Nota final: {grade_total} (promedio de {cuenta} preguntas)")
    input("Enter para continuar...")
    return True

# ==============================
#  CRUD DE ENSAYOS EN evidence.json (misma estructura)
# ==============================
def agregar_ensayo(titulo, autor):
    data = corefiles.read_json(DB_Prueba)
    ensayo = {
        "id": f"PE{len(data['PreguntasEnsayo'])+1}",
        "titulo": titulo,
        "autor": autor,
        "calificacion": None,
        "estado": "Pendiente"
    }
    data["PreguntasEnsayo"].append(ensayo)
    corefiles.write_json(DB_Prueba, data)
    print(f"\n✅ Ensayo '{titulo}' agregado correctamente.")

def listado_ensayos():
    data = corefiles.read_json(DB_Prueba)
    ensayos = data.get("PreguntasEnsayo", [])
    if not ensayos:
        print("\n⚠️ No hay ensayos registrados.")
        return
    print("\n📌 Lista de ensayos:")
    for i, e in enumerate(ensayos, start=1):
        calificacion = e["calificacion"] if e["calificacion"] is not None else "---"
        print(f"{i}. [{e['id']}] Título: {e['titulo']} | Autor: {e['autor']} | Estado: {e['estado']} | Calificación: {calificacion}")

def calificar_ensayo(indice, nota):
    data = corefiles.read_json(DB_Prueba)
    ensayos = data.get("PreguntasEnsayo", [])
    if 0 <= indice < len(ensayos):
        ensayos[indice]["calificacion"] = nota
        ensayos[indice]["estado"] = "Calificado"
        corefiles.write_json(DB_Prueba, data)
        print(f"\n✅ Ensayo '{ensayos[indice]['titulo']}' calificado con {nota}.")
    else:
        print("\n❌ Índice inválido.")
