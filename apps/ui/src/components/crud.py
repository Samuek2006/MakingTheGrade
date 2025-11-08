# apps/components/crud.py  — versión SQLite (sin SQLAlchemy)
from __future__ import annotations
# apps/components/crud.py — versión SQLite (sin encriptado)
from __future__ import annotations
from typing import List, Optional, Dict, Any
from types import SimpleNamespace
import json

from db.db import get_session


# ---------------------------- Helpers ----------------------------

def _parse_opciones(raw) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw]
    s = str(raw).strip()
    if not s:
        return []
    try:
        val = json.loads(s)
        if isinstance(val, list):
            return [str(x) for x in val]
    except Exception:
        pass
    for sep in ["|", ";", ","]:
        if sep in s:
            return [t.strip() for t in s.split(sep) if t.strip()]
    return [s]


def _dump_opciones(lst: List[str] | None) -> str:
    return json.dumps(list(lst or []), ensure_ascii=False)


def _ensure_result_tables(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS prueba_intentos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            prueba_id        INTEGER,
            user_id          INTEGER,
            motivo           TEXT,
            total_preguntas  INTEGER NOT NULL,
            correctas        INTEGER NOT NULL,
            score_pct        REAL NOT NULL,
            finished_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (prueba_id) REFERENCES pruebas(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS prueba_respuestas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            intento_id    INTEGER NOT NULL,
            pregunta_idx  INTEGER NOT NULL,
            seleccion     TEXT,
            correcta      INTEGER,
            FOREIGN KEY (intento_id) REFERENCES prueba_intentos(id) ON DELETE CASCADE
        );
        """
    )


# ---------------------------- USERS ----------------------------

def create_user(identificacion: str, nombre: str, apellido: str,
                telefono: str, username: str, password_plain: str) -> SimpleNamespace:
    """
    Crea usuario sin encriptar la contraseña (guarda texto plano).
    ⚠ Solo usar en desarrollo/test.
    """
    try:
        with get_session() as db:
            cur = db.execute(
                "SELECT id FROM users WHERE identificacion = :identificacion OR username = :username",
                {"identificacion": identificacion, "username": username}
            )
            if cur.fetchone():
                raise ValueError("El usuario ya existe o viola una restricción única.")

            db.execute(
                """
                INSERT INTO users
                    (identificacion, nombre, apellido, telefono, rol, estado, username, password_hash, created_at)
                VALUES
                    (:identificacion, :nombre, :apellido, :telefono, :rol, :estado, :username, :password_plain, datetime('now'))
                """,
                {
                    "identificacion": identificacion,
                    "nombre": nombre,
                    "apellido": apellido,
                    "telefono": telefono,
                    "rol": "student",
                    "estado": "Activo",
                    "username": username,
                    "password_plain": password_plain,  # sin hash
                }
            )
            new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

            row = db.execute(
                """
                SELECT id, identificacion, nombre, apellido, telefono, rol, estado, username
                FROM users WHERE id = :id
                """,
                {"id": new_id}
            ).fetchone()

            return SimpleNamespace(**dict(row))
    except Exception as ex:
        raise ValueError(f"Error al crear usuario: {ex}") from ex


def authenticate_user(username: str, password_plain: str) -> SimpleNamespace:
    """
    Autentica usuario comparando directamente contraseñas sin hash.
    ⚠ Solo usar en desarrollo/test.
    """
    u = (username or "").strip()
    if not u:
        raise ValueError("Usuario requerido.")

    try:
        with get_session() as db:
            row = db.execute(
                """
                SELECT id, nombre, rol, username, estado, password_hash
                FROM users
                WHERE lower(username) = lower(:u)
                """,
                {"u": u}
            ).fetchone()

            if not row:
                raise ValueError("Usuario o contraseña incorrectos.")

            if row["estado"] and str(row["estado"]).lower() != "activo":
                raise ValueError("Tu usuario está inactivo. Contacta al administrador.")

            ph = str(row["password_hash"] or "")
            if password_plain != ph:
                raise ValueError("Usuario o contraseña incorrectos.")

            return SimpleNamespace(
                id=row["id"],
                nombre=row["nombre"],
                rol=row["rol"],
                username=row["username"],
            )
    except Exception as ex:
        raise ValueError(f"No se pudo validar credenciales: {ex}")


# ---------------------------- PRUEBAS (READ) ----------------------------

def get_pruebas_activas(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lista de pruebas activas.
    """
    try:
        with get_session() as db:
            cur = db.execute(
                """
                SELECT id, titulo, descripcion, categoria, estado, duracion_seg, created_at
                FROM pruebas
                WHERE estado = 'Activo'
                ORDER BY created_at DESC
                LIMIT :limit
                """,
                {"limit": int(limit)}
            )
            rows = cur.fetchall()

            out = []
            for r in rows:
                d = dict(r)
                out.append({
                    "id": d["id"],
                    "titulo": d.get("titulo") or d.get("nombre") or f"Prueba {d['id']}",
                    "subtitulo": d.get("descripcion") or d.get("subtitulo") or "",
                    "categoria": d.get("categoria"),
                    "duracion_seg": d.get("duracion_seg"),
                    "estado": d.get("estado"),
                })
            return out
    except Exception as ex:
        print("[CRUD_PRUEBAS] Error consultando pruebas:", ex)
        return []


def get_prueba_by_id(prueba_id: int) -> Optional[Dict[str, Any]]:
    try:
        with get_session() as db:
            r = db.execute(
                """
                SELECT id, titulo, descripcion, categoria, estado, duracion_seg, created_at
                FROM pruebas
                WHERE id = :id
                """,
                {"id": int(prueba_id)}
            ).fetchone()
            if not r:
                return None
            d = dict(r)
            return {
                "id": d["id"],
                "titulo": d.get("titulo") or d.get("nombre") or f"Prueba {d['id']}",
                "subtitulo": d.get("descripcion") or d.get("subtitulo") or "",
                "categoria": d.get("categoria"),
                "duracion_seg": d.get("duracion_seg"),
                "estado": d.get("estado"),
            }
    except Exception as ex:
        print("[CRUD_PRUEBAS] Error get_prueba_by_id:", ex)
        return None


def get_preguntas_by_prueba(prueba_id: int) -> List[Dict[str, Any]]:
    """
    Retorna preguntas de una prueba en orden (si existe columna 'orden').
    """
    try:
        with get_session() as db:
            # Ordena por 'orden' (NULL al final)
            cur = db.execute(
                """
                SELECT id, prueba_id, enunciado, secuencia, opciones_json, correcta, orden
                FROM preguntas
                WHERE prueba_id = :pid
                ORDER BY (orden IS NULL), orden ASC
                """,
                {"pid": int(prueba_id)}
            )
            rows = cur.fetchall()

            out = []
            for r in rows:
                d = dict(r)
                out.append({
                    "id": d["id"],
                    "enunciado": d.get("enunciado") or "",
                    "secuencia": d.get("secuencia"),
                    "opciones": _parse_opciones(d.get("opciones_json", "")),
                    "correcta": d.get("correcta"),
                    "orden": d.get("orden"),
                })
            return out
    except Exception as ex:
        print("[CRUD_PRUEBAS] Error get_preguntas_by_prueba:", ex)
        return []


def get_prueba_con_preguntas(prueba_id: int) -> Optional[Dict[str, Any]]:
    pr = get_prueba_by_id(prueba_id)
    if not pr:
        return None
    pr["preguntas"] = get_preguntas_by_prueba(prueba_id)
    return pr


# ---------------------------- PRUEBAS (CREATE/UPDATE/DELETE) ----------------------------

def create_prueba(titulo: Optional[str] = None,
                  descripcion: Optional[str] = None,
                  estado: str = "Activo",
                  categoria: Optional[str] = None,
                  duracion_seg: Optional[int] = None,
                  duracion_min: Optional[int] = None) -> Dict[str, Any]:
    """
    Crea una prueba. Guarda en columnas existentes del DDL SQLite.
    """
    try:
        with get_session() as db:
            dur_seg = None
            if duracion_seg is not None:
                dur_seg = int(duracion_seg)
            elif duracion_min is not None:
                dur_seg = int(duracion_min) * 60

            db.execute(
                """
                INSERT INTO pruebas (titulo, descripcion, categoria, estado, duracion_seg, created_at)
                VALUES (:titulo, :descripcion, :categoria, :estado, :duracion_seg, datetime('now'))
                """,
                {
                    "titulo": titulo or "Nueva prueba",
                    "descripcion": descripcion or "",
                    "categoria": categoria,
                    "estado": estado,
                    "duracion_seg": dur_seg
                }
            )
            new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            return get_prueba_by_id(new_id)
    except Exception as ex:
        raise ValueError(f"Error creando prueba: {ex}") from ex


def update_prueba_fields(prueba_id: int, **fields) -> Dict[str, Any]:
    """
    Actualiza campos sueltos de Prueba.
    Campos aceptados: titulo, descripcion, estado, categoria, duracion_seg
    (si te pasan 'duracion_min', lo convierto a seg).
    """
    allowed = {"titulo", "descripcion", "estado", "categoria", "duracion_seg", "duracion_min"}
    upd_raw = {k: v for k, v in fields.items() if k in allowed}
    if not upd_raw:
        raise ValueError("No hay campos válidos para actualizar en Prueba.")

    # Normalizar duracion
    if "duracion_min" in upd_raw and "duracion_seg" not in upd_raw:
        try:
            upd_raw["duracion_seg"] = int(upd_raw.pop("duracion_min")) * 60
        except Exception:
            upd_raw.pop("duracion_min", None)

    sets = []
    params = {"id": int(prueba_id)}
    for i, (k, v) in enumerate(upd_raw.items(), start=1):
        sets.append(f"{k} = :v{i}")
        params[f"v{i}"] = v

    sql = f"UPDATE pruebas SET {', '.join(sets)} WHERE id = :id"

    try:
        with get_session() as db:
            db.execute(sql, params)
        out = get_prueba_by_id(prueba_id)
        if not out:
            raise ValueError("Prueba no encontrada luego de actualizar.")
        return out
    except Exception as ex:
        raise ValueError(f"Error actualizando prueba: {ex}") from ex


def delete_prueba(prueba_id: int) -> None:
    try:
        with get_session() as db:
            db.execute("DELETE FROM pruebas WHERE id = :id", {"id": int(prueba_id)})
    except Exception as ex:
        raise ValueError(f"Error eliminando prueba: {ex}") from ex


# ---------------------------- PREGUNTAS (CREATE/UPDATE/DELETE) ----------------------------

def create_pregunta(prueba_id: int,
                    enunciado: str,
                    opciones: List[str],
                    correcta: Optional[str] = None,
                    secuencia: Optional[str] = None,
                    orden: Optional[int] = None) -> Dict[str, Any]:
    """
    Crea pregunta para una prueba. Guarda opciones como JSON en 'opciones_json'.
    """
    try:
        with get_session() as db:
            db.execute(
                """
                INSERT INTO preguntas
                    (prueba_id, enunciado, secuencia, opciones_json, correcta, orden, created_at)
                VALUES
                    (:prueba_id, :enunciado, :secuencia, :opciones_json, :correcta, :orden, datetime('now'))
                """,
                {
                    "prueba_id": int(prueba_id),
                    "enunciado": enunciado,
                    "secuencia": secuencia,
                    "opciones_json": _dump_opciones(opciones),
                    "correcta": correcta,
                    "orden": (int(orden) if orden is not None else None),
                }
            )
            new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]

            r = db.execute(
                """
                SELECT id, prueba_id, enunciado, secuencia, opciones_json, correcta, orden
                FROM preguntas WHERE id = :id
                """,
                {"id": new_id}
            ).fetchone()

            d = dict(r)
            return {
                "id": d["id"],
                "prueba_id": d["prueba_id"],
                "enunciado": d.get("enunciado", ""),
                "secuencia": d.get("secuencia"),
                "opciones": _parse_opciones(d.get("opciones_json", "")),
                "correcta": d.get("correcta"),
                "orden": d.get("orden"),
            }
    except Exception as ex:
        raise ValueError(f"Error creando pregunta: {ex}") from ex


def update_pregunta_fields(pregunta_id: int, **fields) -> Dict[str, Any]:
    """
    Actualiza campos sueltos de Pregunta. Si pasas 'opciones' como list, se serializa a JSON.
    """
    allowed_map = {
        "enunciado": "enunciado",
        "secuencia": "secuencia",
        "correcta": "correcta",
        "respuesta_correcta": "correcta",  # unificamos en 'correcta'
        "orden": "orden",
        "opciones": "opciones_json",
    }

    upd = {}
    for k, v in fields.items():
        if k in allowed_map:
            mapped = allowed_map[k]
            if k == "opciones":
                v = _dump_opciones(v if isinstance(v, list) else _parse_opciones(v))
            upd[mapped] = v

    if not upd:
        raise ValueError("No hay campos válidos para actualizar en Pregunta.")

    sets = []
    params = {"id": int(pregunta_id)}
    for i, (k, v) in enumerate(upd.items(), start=1):
        sets.append(f"{k} = :v{i}")
        params[f"v{i}"] = v

    sql = f"UPDATE preguntas SET {', '.join(sets)} WHERE id = :id"

    try:
        with get_session() as db:
            db.execute(sql, params)
            r = db.execute(
                """
                SELECT id, prueba_id, enunciado, secuencia, opciones_json, correcta, orden
                FROM preguntas WHERE id = :id
                """,
                {"id": int(pregunta_id)}
            ).fetchone()
            if not r:
                raise ValueError("Pregunta no encontrada luego de actualizar.")

            d = dict(r)
            return {
                "id": d["id"],
                "prueba_id": d["prueba_id"],
                "enunciado": d.get("enunciado", ""),
                "secuencia": d.get("secuencia"),
                "opciones": _parse_opciones(d.get("opciones_json", "")),
                "correcta": d.get("correcta"),
                "orden": d.get("orden"),
            }
    except Exception as ex:
        raise ValueError(f"Error actualizando pregunta: {ex}") from ex


def delete_pregunta(pregunta_id: int) -> None:
    try:
        with get_session() as db:
            db.execute("DELETE FROM preguntas WHERE id = :id", {"id": int(pregunta_id)})
    except Exception as ex:
        raise ValueError(f"Error eliminando pregunta: {ex}") from ex


# ---------------------------- INTENTOS / RESPUESTAS DE PRUEBA ----------------------------

def guardar_respuestas_prueba(
        prueba_id: int,
        total_preguntas: int,
        correctas: int,
        respuestas: List[Dict[str, Any]],
        motivo: str = "finalizado",
        user_id: Optional[int] = None,
) -> int:
    """
    Crea un intento en 'prueba_intentos' y sus 'prueba_respuestas'.

    respuestas: [{"pregunta_idx": int, "seleccion": str, "correcta": bool}, ...]
    Retorna: id del intento creado.
    """
    if not total_preguntas or total_preguntas <= 0:
        raise ValueError("total_preguntas debe ser > 0")

    score_pct = (100.0 * correctas / total_preguntas) if total_preguntas else 0.0

    try:
        with get_session() as db:
            _ensure_result_tables(db)

            # 1) Intento
            cur = db.execute(
                """
                INSERT INTO prueba_intentos
                    (prueba_id, user_id, motivo, total_preguntas, correctas, score_pct, finished_at)
                VALUES
                    (:prueba_id, :user_id, :motivo, :total_preguntas, :correctas, :score_pct, datetime('now'))
                """,
                {
                    "prueba_id": int(prueba_id),
                    "user_id": user_id,
                    "motivo": motivo,
                    "total_preguntas": int(total_preguntas),
                    "correctas": int(correctas),
                    "score_pct": float(score_pct),
                },
            )
            intento_id = cur.lastrowid

            # 2) Respuestas (bulk)
            if respuestas:
                payload = [
                    (
                        int(intento_id),
                        int(r.get("pregunta_idx", 0)),
                        str(r.get("seleccion", "")),
                        1 if bool(r.get("correcta", False)) else 0,
                    )
                    for r in respuestas
                ]
                db.executemany(
                    """
                    INSERT INTO prueba_respuestas
                        (intento_id, pregunta_idx, seleccion, correcta)
                    VALUES
                        (?, ?, ?, ?)
                    """,
                    payload
                )

            return int(intento_id)

    except Exception as ex:
        raise ValueError(f"Error guardando intento/respuestas: {ex}") from ex


def get_resumen_intento(intento_id: int) -> Dict[str, Any]:
    """
    Devuelve el intento y sus respuestas (útil para reportes rápidos).
    """
    try:
        with get_session() as db:
            _ensure_result_tables(db)

            intento = db.execute(
                """
                SELECT id,
                       prueba_id,
                       user_id,
                       motivo,
                       total_preguntas,
                       correctas,
                       score_pct,
                       finished_at
                FROM prueba_intentos
                WHERE id = :id
                """,
                {"id": int(intento_id)}
            ).fetchone()

            if not intento:
                raise ValueError("Intento no encontrado.")

            respuestas = db.execute(
                """
                SELECT id, intento_id, pregunta_idx, seleccion, correcta
                FROM prueba_respuestas
                WHERE intento_id = :id
                ORDER BY pregunta_idx ASC
                """,
                {"id": int(intento_id)}
            ).fetchall()

            return {
                "intento": dict(intento),
                "respuestas": [dict(r) for r in respuestas],
            }

    except Exception as ex:
        raise ValueError(f"Error consultando intento/respuestas: {ex}") from ex
