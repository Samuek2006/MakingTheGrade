import json
from datetime import datetime

import util.corefiles as corefiles
import util.utilidades as util
import util.session as session

# ----------------------------
# Rutas de BD
# ----------------------------
DB_Prueba = 'data/evidence.json'
DB_Resultados = 'data/grades.json'

# ----------------------------
# Inicialización de archivos
# ----------------------------
corefiles.initialize_json(DB_Prueba, {
    "PreguntasCerradas": [],
    "PreguntasCortas": [],
    "PreguntasEnsayo": []
})

# IMPORTANTE: Tipos como diccionario (no listas) para usar update_json
corefiles.initialize_json(DB_Resultados, {
    "Resultados": {
        "Cerradas": {},   # clave: identificacion -> payload (o lista si luego quieres historial)
        "Cortas":   {},
        "Ensayo":   {}
    }
})

def asegurar_diccionarios_en_resultados():
    """
    Si grades.json ya existe con listas en Resultados.*,
    migra a diccionarios para que update_json funcione.
    """
    data = corefiles.read_json(DB_Resultados) or {}
    resultados = data.setdefault("Resultados", {})
    for k in ("Cerradas", "Cortas", "Ensayo"):
        v = resultados.get(k)
        if isinstance(v, list):
            # migra: la lista antigua se mapea a dict por índices
            resultados[k] = {str(i): itm for i, itm in enumerate(v)}
        elif v is None:
            resultados[k] = {}
    # Guardar cambios si hubo
    if hasattr(corefiles, "write_json"):
        corefiles.write_json(DB_Resultados, data)
    elif hasattr(corefiles, "save_json"):
        corefiles.save_json(DB_Resultados, data)
    else:
        with open(DB_Resultados, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# Asegura estructura correcta al iniciar
asegurar_diccionarios_en_resultados()

# ----------------------------
# Helpers de guardado
# ----------------------------
def _identificacion_actual():
    # Usa la sesión provista: session.session["user"]
    return session.session.get("user") or "anonimo"

def guardar_resultado_cerradas(resultado: dict):
    """
    Guarda un resultado calificado de Selección Múltiple.
    Estructura: Resultados.Cerradas[identificacion] = { ... }
    """
    payload = {
        "datetime": datetime.now().isoformat(timespec="seconds"),
        **resultado  # contiene puntos, total, score_pct, details, answers
    }
    identificacion = _identificacion_actual()
    asegurar_diccionarios_en_resultados()
    corefiles.update_json(
        DB_Resultados,
        {identificacion: payload},
        ["Resultados", "Cerradas"]
    )

def guardar_respuestas(tipo: str, respuestas: dict, total: int):
    """
    Guarda solo respuestas (sin calificar) para Cortas/Ensayo.
    tipo -> 'Cortas' | 'Ensayo'
    Estructura: Resultados.<tipo>[identificacion] = { datetime, answers, total_questions }
    """
    payload = {
        "datetime": datetime.now().isoformat(timespec="seconds"),
        "answers": respuestas,
        "total_questions": total
    }
    identificacion = _identificacion_actual()
    asegurar_diccionarios_en_resultados()
    corefiles.update_json(
        DB_Resultados,
        {identificacion: payload},
        ["Resultados", tipo]
    )

# ----------------------------
# Menú principal
# ----------------------------
def menuStudent():
    while True:
        try:
            print("""
1. Presentar Prueba Seleccion Multiple
2. Presentar Prueba Preguntas Abiertas (Cortas)
3. Presentar Prueba de Ensayo
4. Calificacion Examen (resumen)
0. Salir
""")
            opcion = int(input('Ingresa una Opcion: '))
            match opcion:
                case 1:
                    util.Limpiar_consola()
                    pruebaSeleccion(DB_Prueba)
                    util.Stop()
                    util.Limpiar_consola()

                case 2:
                    util.Limpiar_consola()
                    pruebaCorta(DB_Prueba)
                    util.Stop()
                    util.Limpiar_consola()

                case 3:
                    util.Limpiar_consola()
                    pruebaEnsayo()
                    util.Stop()
                    util.Limpiar_consola()

                case 4:
                    util.Limpiar_consola()
                    calificacionExamen()
                    util.Stop()
                    util.Limpiar_consola()

                case 0:
                    print('Saliendo del Sistema...')
                    util.Stop()
                    util.Limpiar_consola()
                    break

                case _:
                    print('Ingresa una opcion valida (0 - 4)')
                    util.Stop()
                    util.Limpiar_consola()

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

# ----------------------------
# Prueba Selección Múltiple (califica)
# ----------------------------
def pruebaSeleccion(DB_Prueba: str):
    """
    Visor de examen para PreguntasCerradas:
    - Responder con a/b/c/d  -> guarda y avanza a la siguiente
    - 'n' siguiente           -> avanza sin responder
    - 'p' anterior            -> retrocede
    - 'f' finalizar y calificar (GUARDA en DB_Resultados)
    - 'q' salir sin calificar
    """
    data = corefiles.read_json(DB_Prueba)
    preguntas = data.get("PreguntasCerradas", [])
    total = len(preguntas)

    if total == 0:
        print("⚠️ No hay preguntas disponibles en PreguntasCerradas.")
        return None

    respuestas = {}  # {"Q1": "a", ...}
    index = 0

    while True:
        try:
            pregunta = preguntas[index]
            idPregunta = pregunta.get("id", f"Q{index+1}")
            textoPregunta = pregunta.get("text", "Pregunta sin texto")
            opcionesPreguntas = pregunta.get("options", {})
            repuestaUser = respuestas.get(idPregunta)

            util.Limpiar_consola()
            print(f"📌 Pregunta {index+1}/{total}")
            print(textoPregunta)

            for k in ["a", "b", "c", "d"]:
                if k in opcionesPreguntas:
                    print(f"  {k}) {opcionesPreguntas[k]}")

            if repuestaUser:
                print(f"\n✅ Respuesta guardada: {repuestaUser}")

            print("\n👉 Escribe a/b/c/d para responder (auto-avanza)")
            print("   'n' = siguiente | 'p' = anterior | 'f' = finalizar y calificar | 'q' = salir sin calificar")
            opcion = input("Tu elección: ").strip().lower()

            if opcion in ["a", "b", "c", "d"]:
                if opcion in opcionesPreguntas:
                    respuestas[idPregunta] = opcion
                    if index < total - 1:
                        index += 1
                        continue
                    else:
                        print(f"✅ Respuesta '{opcion}' guardada para {idPregunta}.")
                        print("📌 Ya estás en la última pregunta. Usa 'f' para finalizar o 'p' para revisar.")
                        util.Stop()
                else:
                    print("❌ Esa opción no existe en esta pregunta.")
                    util.Stop()

            elif opcion == "n":
                if index < total - 1:
                    index += 1
                else:
                    print("⚠️ Ya estás en la última pregunta.")
                    util.Stop()

            elif opcion == "p":
                if index > 0:
                    index -= 1
                else:
                    print("⚠️ Ya estás en la primera pregunta.")
                    util.Stop()

            elif opcion == "f":
                util.Limpiar_consola()
                resultado = calificarPreguntas(preguntas, respuestas)
                imprimirResultado(resultado)
                guardar_resultado_cerradas(resultado)  # <-- guarda calificación
                print("💾 Resultado guardado en data/grades.json -> Resultados.Cerradas")
                util.Stop()
                return resultado

            elif opcion == "q":
                print("\n🚪 Saliendo sin calificar...")
                return None

            else:
                print("❌ Opción inválida.")
                util.Stop()

        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando.")
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando.")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            util.Stop()

# ----------------------------
# Preguntas Cortas (NO califica, solo guarda respuestas)
# ----------------------------
def pruebaCorta(DB_Prueba: str):
    data = corefiles.read_json(DB_Prueba)
    preguntas = data.get("PreguntasCortas", [])
    total = len(preguntas)

    if total == 0:
        print("⚠️ No hay preguntas disponibles en PreguntasCortas.")
        return None

    respuestas = {}  # {"PC1": "xxxx", ...}
    index = 0

    while True:
        try:
            pregunta = preguntas[index]
            idPregunta = pregunta.get("id", f"PC{index+1}")
            textoPregunta = pregunta.get("text", "Pregunta sin texto")
            repuestaUser = respuestas.get(idPregunta)

            util.Limpiar_consola()
            print(f"📌 Pregunta {index+1}/{total}")
            print(textoPregunta)

            if repuestaUser:
                print(f"\n✅ Respuesta guardada: {repuestaUser}")

            print("\n👉 Preguntas Abiertas (se guarda tu texto y auto-avanza)")
            print("   'n' = siguiente | 'p' = anterior | 'f' = finalizar y GUARDAR | 'q' = salir sin guardar")
            opcion = input("Tu respuesta: ").strip()

            if opcion.lower() == "n":
                if index < total - 1:
                    index += 1
                else:
                    print("⚠️ Ya estás en la última pregunta.")
                    util.Stop()

            elif opcion.lower() == "p":
                if index > 0:
                    index -= 1
                else:
                    print("⚠️ Ya estás en la primera pregunta.")
                    util.Stop()

            elif opcion.lower() == "f":
                util.Limpiar_consola()
                guardar_respuestas("Cortas", respuestas, total)  # <-- guarda sin calificar
                print("💾 Respuestas guardadas en data/grades.json -> Resultados.Cortas")
                util.Stop()
                return {
                    "answers": respuestas,
                    "total_questions": total
                }

            elif opcion.lower() == "q":
                print("\n🚪 Saliendo sin guardar...")
                return None

            else:
                respuestas[idPregunta] = opcion
                if index < total - 1:
                    index += 1
                    continue
                else:
                    print(f"✅ Respuesta guardada para {idPregunta}.")
                    print("📌 Ya estás en la última pregunta. Usa 'f' para finalizar o 'p' para revisar.")
                    util.Stop()

        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando.")
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando.")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            util.Stop()

# ----------------------------
# Ensayo (NO califica, solo guarda respuestas)
# ----------------------------
def pruebaEnsayo():
    data = corefiles.read_json(DB_Prueba)
    preguntas = data.get("PreguntasEnsayo", [])
    total = len(preguntas)

    if total == 0:
        print("⚠️ No hay preguntas disponibles en PreguntasEnsayo.")
        return None

    respuestas = {}  # {"PE1": "xxxx", ...}
    index = 0

    while True:
        try:
            pregunta = preguntas[index]
            idPregunta = pregunta.get("id", f"PE{index+1}")
            textoPregunta = pregunta.get("text", "Pregunta sin texto")
            repuestaUser = respuestas.get(idPregunta)

            util.Limpiar_consola()
            print(f"📌 Pregunta {index+1}/{total}")
            print(textoPregunta)

            if repuestaUser:
                print(f"\n✅ Respuesta guardada: {repuestaUser}")

            print("\n👉 Ensayo (se guarda tu texto y auto-avanza)")
            print("   'n' = siguiente | 'p' = anterior | 'f' = finalizar y GUARDAR | 'q' = salir sin guardar")
            opcion = input("Tu respuesta: ").strip()

            if opcion.lower() == "n":
                if index < total - 1:
                    index += 1
                else:
                    print("⚠️ Ya estás en la última pregunta.")
                    util.Stop()

            elif opcion.lower() == "p":
                if index > 0:
                    index -= 1
                else:
                    print("⚠️ Ya estás en la primera pregunta.")
                    util.Stop()

            elif opcion.lower() == "f":
                util.Limpiar_consola()
                guardar_respuestas("Ensayo", respuestas, total)  # <-- guarda sin calificar
                print("💾 Respuestas guardadas en data/grades.json -> Resultados.Ensayo")
                util.Stop()
                return {
                    "answers": respuestas,
                    "total_questions": total
                }

            elif opcion.lower() == "q":
                print("\n🚪 Saliendo sin guardar...")
                return None

            else:
                respuestas[idPregunta] = opcion
                if index < total - 1:
                    index += 1
                    continue
                else:
                    print(f"✅ Respuesta guardada para {idPregunta}.")
                    print("📌 Ya estás en la última pregunta. Usa 'f' para finalizar o 'p' para revisar.")
                    util.Stop()

        except KeyboardInterrupt:
            print("\n⛔ Interrupción detectada (Ctrl+C). Cerrando.")
            return None
        except EOFError:
            print("\n⛔ Entrada inesperada (Ctrl+D / Ctrl+Z). Cerrando.")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            util.Stop()

# ----------------------------
# Calificador base (usado solo en Cerradas)
# ----------------------------
def calificarPreguntas(preguntas: list, respuestas: dict):
    """
    Retorna dict con:
    - puntosConjuntos_points, total_points, score_pct
    - details: lista por pregunta con (id, correct, user, is_correct, points)
    - answers: respuestas del usuario
    """
    puntosConjuntos = 0
    total = 0
    detalles = []

    for i, q in enumerate(preguntas, start=1):
        idPregunta = q.get("id", f"Q{i}")
        preguntasCorrectas = str(q.get("correct", "")).strip().lower()
        puntosCorrectos = int(q.get("points ", 1))
        total += puntosCorrectos

        user = str(respuestas.get(idPregunta, "")).strip().lower()
        is_ok = (user == preguntasCorrectas) if preguntasCorrectas else False
        if is_ok:
            puntosConjuntos += puntosCorrectos

        detalles.append({
            "id": idPregunta,
            "correct": preguntasCorrectas or None,
            "user": user or None,
            "is_correct": is_ok,
            "points": puntosCorrectos
        })

    puntajeFinal = round((puntosConjuntos / total) * 100, 2) if total else 0.0
    return {
        "puntosConjuntos_points": puntosConjuntos,
        "total_points": total,
        "score_pct": puntajeFinal,
        "details": detalles,
        "answers": respuestas
    }

# ----------------------------
# Impresión de resultados (solo Cerradas)
# ----------------------------
def imprimirResultado(resultado: dict):
    print("📊 Resultado del examen (Selección múltiple)")
    print(f"   Puntaje: {resultado['puntosConjuntos_points']} / {resultado['total_points']}  ({resultado['score_pct']}%)\n")
    print("🧾 Detalle por pregunta:")
    for d in resultado["details"]:
        marca = "✅" if d["is_correct"] else "❌"
        print(f" - {d['id']}: {marca} (resp: {d['user']}, correcta: {d['correct']}, puntos: {d['points']})")
    print("\n✅ Fin de la calificación.")
    input('Enter para continuar...')

# ----------------------------
# Opción 4: Resumen de calificaciones / envíos
# ----------------------------
def calificacionExamen():
    data = corefiles.read_json(DB_Resultados) or {}
    resultados = data.get("Resultados", {})

    def resumen_tipo(nombre_tipo, contenedor):
        print(f"\n=== {nombre_tipo} ===")
        if not isinstance(contenedor, dict) or not contenedor:
            print("   (sin envíos)")
            return
        # Muestra último envío del usuario actual si existe
        ident = _identificacion_actual()
        if ident in contenedor:
            ultimo = contenedor[ident]
            if nombre_tipo == "Cerradas":
                pts = ultimo.get("puntosConjuntos_points", 0)
                tot = ultimo.get("total_points", 0)
                pct = ultimo.get("score_pct", 0)
                when = ultimo.get("datetime")
                print(f"   Último intento [{ident}] -> {when} | Puntaje: {pts}/{tot} ({pct}%)")
            else:
                when = ultimo.get("datetime")
                n = len((ultimo.get("answers") or {}).keys())
                print(f"   Último envío [{ident}] -> {when} | Preguntas respondidas: {n}")
        else:
            print("   (no hay envíos para el usuario actual)")

        # Conteo simple
        print(f"   Total de usuarios con registros: {len(contenedor)}")

    print("📚 Resumen de resultados (data/grades.json)")
    resumen_tipo("Cerradas", resultados.get("Cerradas", {}))
    resumen_tipo("Cortas",   resultados.get("Cortas",   {}))
    resumen_tipo("Ensayo",   resultados.get("Ensayo",   {}))
    input("\nEnter para continuar...")
