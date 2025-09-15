import util.corefiles as corefiles
import util.utilidades as utilidades
import json

DB_Prueba = 'data/evidence.json'
corefiles.initialize_json(DB_Prueba, {
    "PreguntasCerradas": [],
    "PreguntasCortas": [],
    "PreguntasEnsayo": []
})

DB_Qualifer = 'data/grades.json'
corefiles.initialize_json(DB_Qualifer, {
    "Qualifer_ensayos": {}
})


def menuQualifier():
    while True:
        print("\n===== MENÚ ENSAYOS =====")
        print("1. Agregar ensayo")
        print("2. Listar ensayos")
        print("3. Calificar ensayo")
        print("4. Salir")

        opcion = input("👉 Selecciona una opción: ")

        if opcion == "1":
            titulo = input("Título del ensayo: ")
            autor = input("Autor del ensayo: ")
            agregar_ensayo(titulo, autor)

        elif opcion == "2":
            listado_ensayos()

        elif opcion == "3":
            listado_ensayos()
            try:
                indice = int(input("Número del ensayo a calificar: ")) - 1
                nota = int(input("Nota (0 - 100): "))
                calificar_ensayo(indice, nota)   # ✅ directo
            except ValueError:
                print("❌ Entrada inválida. Intenta de nuevo.")

        elif opcion == "4":
            print("\n👋 Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida, intenta de nuevo.")


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
    for i, ensayo in enumerate(ensayos, start=1):
        calificacion = ensayo["calificacion"] if ensayo["calificacion"] is not None else "---"
        print(f"{i}. [{ensayo['id']}] Título: {ensayo['titulo']} | Autor: {ensayo['autor']} | Estado: {ensayo['estado']} | Calificación: {calificacion}")


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
