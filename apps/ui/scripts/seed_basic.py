"""
Seed básico para la base de datos SQLite local.

Creará:
- Usuario de prueba: usuario=Andres1234, contraseña=123456
- 2 pruebas activas con algunas preguntas de ejemplo

Uso:
  python3 scripts/seed_basic.py
"""
from __future__ import annotations
import json
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None

import sys
from pathlib import Path

# Asegura que el directorio raíz del proyecto esté en sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db.db import init_db, get_session
from passlib.hash import pbkdf2_sha256


def ensure_user() -> int:
    username = "Andres1234"
    password = "123456"
    password_h = pbkdf2_sha256.hash(password)
    with get_session() as db:
        row = db.execute(
            "SELECT id FROM users WHERE lower(username)=lower(:u)", {"u": username}
        ).fetchone()
        if row:
            return int(row["id"])

        db.execute(
            """
            INSERT INTO users
                (identificacion, nombre, apellido, telefono, rol, estado, username, password_hash)
            VALUES
                (:identificacion, :nombre, :apellido, :telefono, :rol, :estado, :username, :password)
            """,
            {
                "identificacion": "1234567890",
                "nombre": "Andres",
                "apellido": "Pérez",
                "telefono": "+57 3000000000",
                "rol": "student",
                "estado": "Activo",
                "username": username,
                "password": password_h,
            },
        )
        new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        return int(new_id)


def ensure_prueba(titulo: str, descripcion: str, duracion_seg: int) -> int:
    with get_session() as db:
        row = db.execute(
            "SELECT id FROM pruebas WHERE titulo = :t", {"t": titulo}
        ).fetchone()
        if row:
            return int(row["id"])

        db.execute(
            """
            INSERT INTO pruebas (titulo, descripcion, categoria, estado, duracion_seg)
            VALUES (:titulo, :descripcion, :categoria, 'Activo', :duracion)
            """,
            {"titulo": titulo, "descripcion": descripcion, "categoria": "General", "duracion": int(duracion_seg)},
        )
        new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        return int(new_id)


def ensure_pregunta(prueba_id: int, orden: int, enunciado: str, opciones: list[str], correcta: str) -> None:
    with get_session() as db:
        row = db.execute(
            "SELECT id FROM preguntas WHERE prueba_id=:pid AND orden=:o",
            {"pid": int(prueba_id), "o": int(orden)},
        ).fetchone()
        if row:
            return

        db.execute(
            """
            INSERT INTO preguntas (prueba_id, enunciado, secuencia, opciones_json, correcta, orden, estado)
            VALUES (:pid, :enun, :seq, :opts, :corr, :orden, 'Activo')
            """,
            {
                "pid": int(prueba_id),
                "enun": enunciado,
                "seq": str(orden),
                "opts": json.dumps(opciones, ensure_ascii=False),
                "corr": correcta,
                "orden": int(orden),
            },
        )


def main() -> int:
    if load_dotenv:
        load_dotenv()

    # Crea archivo y tablas si no existen
    init_db(create_all=True)

    user_id = ensure_user()

    p1 = ensure_prueba(
        titulo="Matemáticas Básicas",
        descripcion="Operaciones aritméticas sencillas",
        duracion_seg=600,
    )
    ensure_pregunta(p1, 1, "¿Cuánto es 2 + 2?", ["A) 4", "B) 3", "C) 5", "D) 22"], "A")
    ensure_pregunta(p1, 2, "¿Cuánto es 5 - 3?", ["A) 1", "B) 2", "C) 3", "D) 8"], "B")

    p2 = ensure_prueba(
        titulo="Comprensión Lectora",
        descripcion="Preguntas de comprensión simples",
        duracion_seg=900,
    )
    ensure_pregunta(p2, 1, "Selecciona el sinónimo de 'rápido'", ["A) veloz", "B) lento", "C) tarde", "D) igual"], "A")
    ensure_pregunta(p2, 2, "Selecciona el antónimo de 'frío'", ["A) helado", "B) tibio", "C) caliente", "D) igual"], "C")

    print("Seed completado. Usuario de prueba: Andres1234 / 123456")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
