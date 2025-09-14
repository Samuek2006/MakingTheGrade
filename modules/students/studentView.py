import util.corefiles as corefiles
import util.utilidades as util
import util.session as session
import json

DB_Prueba = 'data/evidence.json'
corefiles.initialize_json(DB_Prueba, {
    "PreguntasCerradas" : [],
    "PreguntasCortas" : [],
    "PreguntasEnsayo" : []
})

def menuStudent():
    while True:
        try:
            print("""
1. Presentar Prueba Seleccion Multiple
2. Presentar Prueba Preguntas Abiertas
3. Presentar Prueba de Ensayo
4. Calificacion Examen
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
                    print("🔧 Próximamente: Preguntas Abiertas")
                    util.Stop()
                    util.Limpiar_consola()

                case 3:
                    print("🔧 Próximamente: Ensayo")
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
                    print('Ingresa una opcion valida (0 - 3)')
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

def pruebaSeleccion(DB_Prueba: str):
    """
    Visor de examen para PreguntasCerradas:
    - Responder con a/b/c/d  -> guarda y avanza a la siguiente
    - 'n' siguiente           -> avanza sin responder
    - 'p' anterior            -> retrocede
    - 'f' finalizar y calificar
    - 'q' salir sin calificar
    """
    # Cargar BD de preguntas
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
            ya = respuestas.get(idPregunta)

            util.Limpiar_consola()
            print(f"📌 Pregunta {index+1}/{total}")
            print(textoPregunta)

            # Muestra opciones permitidas (a-d si existen)
            for k in ["a", "b", "c", "d"]:
                if k in opcionesPreguntas:
                    print(f"  {k}) {opcionesPreguntas[k]}")

            if ya:
                print(f"\n✅ Respuesta guardada: {ya}")

            print("\n👉 Escribe a/b/c/d para responder (auto-avanza)")
            print("   'n' = siguiente | 'p' = anterior | 'f' = finalizar y calificar | 'q' = salir sin calificar")
            opcion = input("Tu elección: ").strip().lower()

            if opcion in ["a", "b", "c", "d"]:
                if opcion in opcionesPreguntas:
                    respuestas[idPregunta] = opcion
                    # Auto-avanza si no es la última
                    if index < total - 1:
                        index += 1
                        # no pausamos para que el flujo sea fluido
                        continue
                    else:
                        # Última pregunta: informar y esperar acción del usuario
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
                # Finalizar y calificar
                util.Limpiar_consola()
                resultado = calificarPreguntas(preguntas, respuestas)
                imprimirResultado(resultado)
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

def calificarPreguntas(preguntas: list, respuestas: dict):
    """
    Retorna dict con:
    - earned_points, total_points, score_pct
    - details: lista por pregunta con (id, correct, user, is_correct, points)
    """
    puntosConjuntos = 0
    total = 0
    detalles = []

    for i, q in enumerate(preguntas, start=1):
        idPregunta = q.get("id", f"Q{i}")
        preguntasCorrectas = str(q.get("correct", "")).strip().lower()
        puntosCorrectos = int(q.get("points", 1))
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


def imprimirResultado(resultado: dict):
    print("📊 Resultado del examen (Selección múltiple)")
    print(f"   Puntaje: {resultado['puntosConjuntos_points']} / {resultado['total_points']}  ({resultado['score_pct']}%)\n")
    print("🧾 Detalle por pregunta:")
    for d in resultado["details"]:
        marca = "✅" if d["is_correct"] else "❌"
        print(f" - {d['id']}: {marca} (resp: {d['user']}, correcta: {d['correct']}, puntos: {d['points']})")
    print("\n✅ Fin de la calificación.")
    input('Enter para continuar...')

def calificacionExamen():
    pass