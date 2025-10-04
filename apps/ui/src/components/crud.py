# apps/components/crud.py
from __future__ import annotations
from typing import List, Optional, Dict, Any
from types import SimpleNamespace
import json

from sqlalchemy import select, func, update, delete, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from passlib.hash import bcrypt

from apps.db.db import get_session
from apps.db.models.models import User, RolEnum, Prueba, Pregunta


# ---------------------------- Helpers ----------------------------

def _parse_opciones(raw) -> List[str]:
    """
    Admite JSON (["A","B"]) o texto con separadores | ; ,
    y retorna lista de strings.
    """
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw]
    s = str(raw).strip()
    if not s:
        return []
    # primero intenta JSON
    try:
        val = json.loads(s)
        if isinstance(val, list):
            return [str(x) for x in val]
    except Exception:
        pass
    # fallback separadores comunes
    for sep in ["|", ";", ","]:
        if sep in s:
            return [t.strip() for t in s.split(sep) if t.strip()]
    return [s]


def _dump_opciones(lst: List[str] | None) -> str:
    """Serializa opciones siempre como JSON para consistencia."""
    return json.dumps(list(lst or []), ensure_ascii=False)


# ---------------------------- USERS ----------------------------

def create_user(identificacion: str, nombre: str, apellido: str,
                telefono: str, username: str, password_hash: str) -> SimpleNamespace:
    try:
        with get_session() as db:
            new = User(
                identificacion=identificacion,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                rol=RolEnum.student,
                estado="Activo",
                username=username,
                password_hash=password_hash,
            )
            db.add(new)
            db.commit()
            db.refresh(new)
            return SimpleNamespace(
                id=new.id,
                identificacion=new.identificacion,
                nombre=new.nombre,
                apellido=new.apellido,
                telefono=new.telefono,
                rol=new.rol,
                estado=new.estado,
                username=new.username,
            )
    except IntegrityError as ex:
        raise ValueError("El usuario ya existe o viola una restricción única.") from ex
    except SQLAlchemyError as ex:
        raise ValueError(f"Error de base de datos al crear usuario: {ex}") from ex


def authenticate_user(username: str, password_plain: str) -> SimpleNamespace:
    u = (username or "").strip()
    if not u:
        raise ValueError("Usuario requerido.")

    try:
        with get_session() as db:
            print("[AUTH] Buscando usuario:", u.lower())
            q = select(User).where(func.lower(User.username) == u.lower())
            user = db.execute(q).scalar_one_or_none()

            if not user:
                print("[AUTH] Usuario no existe")
                raise ValueError("Usuario o contraseña incorrectos.")

            print("[AUTH] Usuario encontrado. id:", user.id, "username:", user.username)

            if getattr(user, "estado", None) and str(user.estado).lower() != "activo":
                print("[AUTH] Usuario inactivo. estado:", user.estado)
                raise ValueError("Tu usuario está inactivo. Contacta al administrador.")

            ph = getattr(user, "password_hash", "") or ""
            print("[AUTH] Largo hash:", len(ph))

            try:
                ok = bcrypt.verify(password_plain, ph)
            except Exception as be:
                print("[AUTH] Error verificando bcrypt:", be)
                raise ValueError(f"Error verificando credenciales: {be}")

            if not ok:
                print("[AUTH] Password incorrecto")
                raise ValueError("Usuario o contraseña incorrectos.")

            print("[AUTH] Password OK")
            return SimpleNamespace(
                id=user.id,
                nombre=user.nombre,
                rol=getattr(user, "rol", None),
                username=user.username,
            )

    except SQLAlchemyError as ex:
        print("[AUTH] SQLAlchemyError:", ex)
        raise ValueError(f"No se pudo validar credenciales. Detalle: {ex}")


# ---------------------------- PRUEBAS (READ) ----------------------------

def get_pruebas_activas(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lista de pruebas activas.
    """
    try:
        with get_session() as db:
            q = (
                select(Prueba)
                .where(Prueba.estado == "Activo")  # cambia si tu valor es "Activa"
                .order_by(Prueba.created_at.desc())
                .limit(limit)
            )
            rows = db.execute(q).scalars().all()

            out = []
            for r in rows:
                out.append({
                    "id": r.id,
                    "titulo": getattr(r, "titulo", getattr(r, "nombre", f"Prueba {r.id}")),
                    "subtitulo": getattr(r, "subtitulo", getattr(r, "descripcion", "")) or "",
                    "categoria": getattr(r, "categoria", None),
                    "duracion_seg": getattr(r, "duracion_seg", None)
                                    or (getattr(r, "duracion_min", None) and int(r.duracion_min) * 60) or None,
                    "estado": getattr(r, "estado", None),
                })
            return out

    except SQLAlchemyError as ex:
        print("[CRUD_PRUEBAS] Error consultando pruebas:", ex)
        return []


def get_prueba_by_id(prueba_id: int) -> Optional[Dict[str, Any]]:
    try:
        with get_session() as db:
            r = db.execute(select(Prueba).where(Prueba.id == prueba_id)).scalar_one_or_none()
            if not r:
                return None
            return {
                "id": r.id,
                "titulo": getattr(r, "titulo", getattr(r, "nombre", f"Prueba {r.id}")),
                "subtitulo": getattr(r, "subtitulo", getattr(r, "descripcion", "")) or "",
                "categoria": getattr(r, "categoria", None),
                "duracion_seg": getattr(r, "duracion_seg", None)
                                or (getattr(r, "duracion_min", None) and int(r.duracion_min) * 60) or None,
                "estado": getattr(r, "estado", None),
            }
    except SQLAlchemyError as ex:
        print("[CRUD_PRUEBAS] Error get_prueba_by_id:", ex)
        return None


def get_preguntas_by_prueba(prueba_id: int) -> List[Dict[str, Any]]:
    """
    Retorna preguntas de una prueba en orden (si existe columna 'orden').
    """
    try:
        with get_session() as db:
            q = select(Pregunta).where(Pregunta.prueba_id == prueba_id)
            # si tienes columna 'orden', respeta el orden
            if hasattr(Pregunta, "orden"):
                q = q.order_by(Pregunta.orden.asc())
            rows = db.execute(q).scalars().all()

            out = []
            for r in rows:
                out.append({
                    "id": r.id,
                    "enunciado": getattr(r, "enunciado", "") or "",
                    "secuencia": getattr(r, "secuencia", None),
                    "opciones": _parse_opciones(getattr(r, "opciones", getattr(r, "opciones_json", ""))),
                    "correcta": getattr(r, "correcta", getattr(r, "respuesta_correcta", None)),
                    "orden": getattr(r, "orden", None),
                })
            return out
    except SQLAlchemyError as ex:
        print("[CRUD_PRUEBAS] Error get_preguntas_by_prueba:", ex)
        return []


def get_prueba_con_preguntas(prueba_id: int) -> Optional[Dict[str, Any]]:
    """
    Agrega prueba + sus preguntas.
    """
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
    Crea una prueba. Usa campo disponible en tu modelo (titulo o nombre, descripcion o subtitulo).
    """
    try:
        with get_session() as db:
            # decide qué atributo usar según tu modelo
            kwargs = {"estado": estado}
            if hasattr(Prueba, "titulo"):
                kwargs["titulo"] = titulo or "Nueva prueba"
            elif hasattr(Prueba, "nombre"):
                kwargs["nombre"] = titulo or "Nueva prueba"

            if hasattr(Prueba, "descripcion"):
                kwargs["descripcion"] = descripcion or ""
            elif hasattr(Prueba, "subtitulo"):
                kwargs["subtitulo"] = descripcion or ""

            if hasattr(Prueba, "categoria"):
                kwargs["categoria"] = categoria

            # duración
            if duracion_seg is not None and hasattr(Prueba, "duracion_seg"):
                kwargs["duracion_seg"] = int(duracion_seg)
            elif duracion_min is not None and hasattr(Prueba, "duracion_min"):
                kwargs["duracion_min"] = int(duracion_min)

            pr = Prueba(**kwargs)
            db.add(pr)
            db.commit()
            db.refresh(pr)
            return get_prueba_by_id(pr.id)  # retorna dict consistente
    except SQLAlchemyError as ex:
        raise ValueError(f"Error creando prueba: {ex}") from ex


def update_prueba_fields(prueba_id: int, **fields) -> Dict[str, Any]:
    """
    Actualiza campos sueltos de Prueba de forma segura.
    Campos aceptados típicos: titulo/nombre, descripcion/subtitulo, estado, categoria, duracion_seg/duracion_min
    """
    allowed = {"titulo", "nombre", "descripcion", "subtitulo", "estado", "categoria", "duracion_seg", "duracion_min"}
    upd = {k: v for k, v in fields.items() if k in allowed}

    if not upd:
        raise ValueError("No hay campos válidos para actualizar en Prueba.")

    try:
        with get_session() as db:
            db.execute(update(Prueba).where(Prueba.id == prueba_id).values(**upd))
            db.commit()
        out = get_prueba_by_id(prueba_id)
        if not out:
            raise ValueError("Prueba no encontrada luego de actualizar.")
        return out
    except SQLAlchemyError as ex:
        raise ValueError(f"Error actualizando prueba: {ex}") from ex


def delete_prueba(prueba_id: int) -> None:
    """
    El borrado en cascada de preguntas depende de tu FK (ON DELETE CASCADE).
    """
    try:
        with get_session() as db:
            db.execute(delete(Prueba).where(Prueba.id == prueba_id))
            db.commit()
    except SQLAlchemyError as ex:
        raise ValueError(f"Error eliminando prueba: {ex}") from ex


# ---------------------------- PREGUNTAS (CREATE/UPDATE/DELETE) ----------------------------

def create_pregunta(prueba_id: int,
                    enunciado: str,
                    opciones: List[str],
                    correcta: Optional[str] = None,
                    secuencia: Optional[str] = None,
                    orden: Optional[int] = None) -> Dict[str, Any]:
    """
    Crea pregunta para una prueba. Guarda opciones como JSON (o al campo que tengas).
    """
    try:
        with get_session() as db:
            kwargs = {
                "prueba_id": prueba_id,
                "enunciado": enunciado,
            }
            # opciones/opciones_json
            if hasattr(Pregunta, "opciones"):
                kwargs["opciones"] = _dump_opciones(opciones)
            elif hasattr(Pregunta, "opciones_json"):
                kwargs["opciones_json"] = _dump_opciones(opciones)

            # correcta/respuesta_correcta
            if hasattr(Pregunta, "correcta"):
                kwargs["correcta"] = correcta
            elif hasattr(Pregunta, "respuesta_correcta"):
                kwargs["respuesta_correcta"] = correcta

            if hasattr(Pregunta, "secuencia"):
                kwargs["secuencia"] = secuencia
            if hasattr(Pregunta, "orden") and orden is not None:
                kwargs["orden"] = int(orden)

            pq = Pregunta(**kwargs)
            db.add(pq)
            db.commit()
            db.refresh(pq)

            return {
                "id": pq.id,
                "prueba_id": pq.prueba_id,
                "enunciado": pq.enunciado,
                "secuencia": getattr(pq, "secuencia", None),
                "opciones": _parse_opciones(getattr(pq, "opciones", getattr(pq, "opciones_json", ""))),
                "correcta": getattr(pq, "correcta", getattr(pq, "respuesta_correcta", None)),
                "orden": getattr(pq, "orden", None),
            }
    except SQLAlchemyError as ex:
        raise ValueError(f"Error creando pregunta: {ex}") from ex


def update_pregunta_fields(pregunta_id: int, **fields) -> Dict[str, Any]:
    """
    Actualiza campos sueltos de Pregunta. Si pasas 'opciones' como list, se serializa a JSON.
    """
    # mapear keys permitidas a campos reales
    allowed_map = {
        "enunciado": "enunciado",
        "secuencia": "secuencia",
        "correcta": "correcta",  # o respuesta_correcta
        "respuesta_correcta": "respuesta_correcta",
        "orden": "orden",
        "opciones": "opciones",  # o opciones_json
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

    # si tu modelo usa 'respuesta_correcta' en lugar de 'correcta'
    if "correcta" in upd and not hasattr(Pregunta, "correcta") and hasattr(Pregunta, "respuesta_correcta"):
        upd["respuesta_correcta"] = upd.pop("correcta")

    if "opciones" in upd and not hasattr(Pregunta, "opciones") and hasattr(Pregunta, "opciones_json"):
        upd["opciones_json"] = upd.pop("opciones")

    try:
        with get_session() as db:
            db.execute(update(Pregunta).where(Pregunta.id == pregunta_id).values(**upd))
            db.commit()
        # devolver la pregunta actualizada
        with get_session() as db:
            r = db.execute(select(Pregunta).where(Pregunta.id == pregunta_id)).scalar_one_or_none()
            if not r:
                raise ValueError("Pregunta no encontrada luego de actualizar.")
            return {
                "id": r.id,
                "prueba_id": r.prueba_id,
                "enunciado": getattr(r, "enunciado", ""),
                "secuencia": getattr(r, "secuencia", None),
                "opciones": _parse_opciones(getattr(r, "opciones", getattr(r, "opciones_json", ""))),
                "correcta": getattr(r, "correcta", getattr(r, "respuesta_correcta", None)),
                "orden": getattr(r, "orden", None),
            }
    except SQLAlchemyError as ex:
        raise ValueError(f"Error actualizando pregunta: {ex}") from ex


def delete_pregunta(pregunta_id: int) -> None:
    try:
        with get_session() as db:
            db.execute(delete(Pregunta).where(Pregunta.id == pregunta_id))
            db.commit()
    except SQLAlchemyError as ex:
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

    sql_insert_intento = text("""
                                INSERT INTO prueba_intentos
                                (prueba_id, user_id, motivo, total_preguntas, correctas, score_pct, finished_at)
                                VALUES (:prueba_id, :user_id, :motivo, :total_preguntas, :correctas, :score_pct, NOW())
                                """)

    sql_last_id = text("SELECT LAST_INSERT_ID() AS id")

    sql_insert_respuesta = text("""
                                INSERT INTO prueba_respuestas
                                    (intento_id, pregunta_idx, seleccion, correcta)
                                VALUES (:intento_id, :pregunta_idx, :seleccion, :correcta)
                                """)

    try:
        with get_session() as db:
            # 1) Intento
            db.execute(
                sql_insert_intento,
                {
                    "prueba_id": int(prueba_id),
                    "user_id": user_id,  # si aún no manejas sesión, pasará None
                    "motivo": motivo,
                    "total_preguntas": int(total_preguntas),
                    "correctas": int(correctas),
                    "score_pct": float(score_pct),
                },
            )
            intento_id = db.execute(sql_last_id).mappings().first()["id"]

            # 2) Respuestas (bulk)
            if respuestas:
                payload = [
                    {
                        "intento_id": int(intento_id),
                        "pregunta_idx": int(r.get("pregunta_idx", 0)),
                        "seleccion": str(r.get("seleccion", "")),
                        "correcta": 1 if bool(r.get("correcta", False)) else 0,
                    }
                    for r in respuestas
                ]
                db.execute(sql_insert_respuesta, payload)  # executemany con lista de dicts

            # commit lo hace get_session()
            return int(intento_id)

    except SQLAlchemyError as ex:
        raise ValueError(f"Error guardando intento/respuestas: {ex}") from ex


def get_resumen_intento(intento_id: int) -> Dict[str, Any]:
    """
    Devuelve el intento y sus respuestas (útil para reportes rápidos).
    """
    try:
        with get_session() as db:
            intento = db.execute(
                text("""
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
                        """),
                {"id": int(intento_id)},
            ).mappings().first()

            if not intento:
                raise ValueError("Intento no encontrado.")

            respuestas = db.execute(
                text("""
                        SELECT id, intento_id, pregunta_idx, seleccion, correcta
                        FROM prueba_respuestas
                        WHERE intento_id = :id
                        ORDER BY pregunta_idx ASC
                        """),
                {"id": int(intento_id)},
            ).mappings().all()

            return {
                "intento": dict(intento),
                "respuestas": [dict(r) for r in respuestas],
            }

    except SQLAlchemyError as ex:
        raise ValueError(f"Error consultando intento/respuestas: {ex}") from ex
