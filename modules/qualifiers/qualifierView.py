import json
from datetime import datetime

import util.corefiles as corefiles
import util.utilidades as utilidades

# === BDs ===
DB_Prueba    = 'data/evidence.json'
DB_Qualifer  = 'data/grades.json'

# === Inicialización (misma estructura, sin POO) ===
corefiles.initialize_json(DB_Prueba, {
    "PreguntasCerradas": [],
    "PreguntasCortas":  [],
    "PreguntasEnsayo":  []
})

corefiles.initialize_json(DB_Qualifer, {
    "Resultados": {          # donde se guardan respuestas/resultado del alumno
        "Cerradas": {},
        "Cortas":   {},
        "Ensayo":   {}
    },
    "Qualifer_ensayos": {    # donde se guarda la calificación del corrector
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
        print("4. Salir")
        opcion = input("👉 Opción: ").strip()

        if opcion == "1":
            listar_pendientes("Cortas")
        elif opcion == "2":
            listar_pendientes("Ensayo")
        elif opcion == "3":
            tipo = input("Tipo (Cortas/Ensayo): ").strip().title()
            if tipo not in ("Cortas", "Ensayo"):
                print("❌ Tipo inválido.")
                continue
            pendientes = listar_pendientes(tipo)
            if not pendientes:
                continue
            try:
                idx  = int(input("Número del pendiente a calificar: ").strip())
                nota = int(input("Nota (0-100): ").strip())
                obs  = input("Observaciones (opcional): ").strip()
            except ValueError:
                print("❌ Entrada inválida.")
                continue
            calificar_pendiente(tipo, idx, nota, obs)
        elif opcion == "4":
            print("\n👋 Saliendo. ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida.")

# ==============================
#  LISTAR Y CALIFICAR PENDIENTES
# ==============================
def _leer_grades():
    data = corefiles.read_json(DB_Qualifer) or {}
    data.setdefault("Resultados", {"Cerradas": {}, "Cortas": {}, "Ensayo": {}})
    data.setdefault("Qualifer_ensayos", {"Cortas": {}, "Ensayo": {}})
    return data

def listar_pendientes(tipo: str):
    data = _leer_grades()
    resultados = data["Resultados"].get(tipo, {}) or {}
    ya_calificados = data["Qualifer_ensayos"].get(tipo, {}) or {}

    # pendientes = ident donde no exista calificación en Qualifer_ensayos ni grade en Resultados
    pendientes = []
    for ident, payload in resultados.items():
        graded_flag = bool(payload.get("graded")) or (ident in ya_calificados) or ("grade" in payload)
        if not graded_flag:
            pendientes.append((ident, payload))

    if not pendientes:
        print(f"\n✅ No hay pendientes en {tipo}.")
        return []

    print(f"\n📌 Pendientes en {tipo}:")
    for i, (ident, payload) in enumerate(pendientes, start=1):
        when = payload.get("datetime", "-")
        answers = payload.get("answers") or {}
        print(f"{i}. [{ident}] {when} | respuestas: {len(answers)}")
    return pendientes

def calificar_pendiente(tipo: str, indice: int, nota: int, observaciones: str = ""):
    pendientes = listar_pendientes(tipo)
    if not pendientes:
        print("⚠️ No hay elementos por calificar.")
        return False
    if indice < 1 or indice > len(pendientes):
        print("❌ Índice inválido.")
        return False

    ident, payload = pendientes[indice - 1]
    now = datetime.now().isoformat(timespec="seconds")

    # 1) Guardar calificación del corrector bajo Qualifer_ensayos.<tipo>.<ident>
    calif_obj = {
        "grade": nota,
        "graded_at": now,
        "observaciones": observaciones,
        "answers": payload.get("answers"),
        "total_questions": payload.get("total_questions")
    }
    corefiles.update_json(DB_Qualifer, {ident: calif_obj}, ["Qualifer_ensayos", tipo])

    # 2) Marcar registro del resultado como calificado y copiar nota
    corefiles.update_json(DB_Qualifer, {"graded": True, "grade": nota}, ["Resultados", tipo, ident])

    print(f"\n✅ Calificado [{tipo}] -> {ident} con nota {nota}.")
    return True

# ==============================
#  CRUD DE ENSAYOS EN evidence.json (tu misma estructura)
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