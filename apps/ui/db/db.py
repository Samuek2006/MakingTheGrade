import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
try:
    from dotenv import load_dotenv
except Exception:
    # Permite ejecutar sin python-dotenv instalado
    def load_dotenv(*args, **kwargs):
        return None

# ============================================
# Cargar variables de entorno desde .env
# ============================================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "192.168.137.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "tester")
DB_PASS = os.getenv("DB_PASS", "Sfelipe2006.")
DB_NAME = os.getenv("DB_NAME", "marking_grade")

# ============================================
# "URLs" de conexión (compat) y ruta de archivo SQLite
# ============================================
BASE_URL_NO_DB = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
DATABASE_URL   = f"{BASE_URL_NO_DB}/{DB_NAME}?charset=utf8mb4"

# Ruta del archivo SQLite (Android-friendly). Puedes sobreescribirla con SQLITE_DB_PATH si quieres.
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH")  # opcional: ruta absoluta
if SQLITE_DB_PATH:
    DB_PATH = Path(SQLITE_DB_PATH).expanduser()
else:
    # Guarda como "<DB_NAME>.db" en el HOME del usuario (en Android funciona bien)
    safe_name = f"{DB_NAME}.db" if not DB_NAME.lower().endswith(".db") else DB_NAME
    DB_PATH = Path.home() / safe_name

# --------------------------------------------
# "engine" y "SessionLocal" de compatibilidad
# --------------------------------------------
class _CompatEngine:
    """Compatibilidad mínima para que exista un 'engine' exportado."""
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connect(self):
        # Ofrece una conexión sqlite3 nativa
        return _connect()

def _connect() -> sqlite3.Connection:
    """Crea conexión sqlite3 con Row factory y FKs habilitados."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Exponemos 'engine' para compatibilidad con código que lo importe.
engine = _CompatEngine(DB_PATH)

def _session_factory():
    """Equivalente simple a 'SessionLocal' devolviendo una conexión sqlite3."""
    return _connect()

# Conservamos el nombre 'SessionLocal' para que los imports no se rompan.
SessionLocal = _session_factory

# 'Base' marcador para no romper imports existentes de tus models
class _CompatBase:
    pass

Base = _CompatBase


def create_database_if_not_exists():
    """
    Compat: en SQLite, crear la 'DB' es crear/abrir el archivo.
    Mantiene la misma firma que tu función original.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        with _connect() as conn:
            pass  # tocar el archivo


def init_db(create_all: bool = False):
    """
    Inicializa la base de datos (compat):
      1) Crea el archivo .db si no existe.
      2) Si create_all=True, crea todas las tablas ejecutando el DDL de tus models:
         - Importa SCHEMA_SQL desde db.models.models (tu ruta original de models.py).
    """
    create_database_if_not_exists()

    if create_all:
        try:
            # 👇 Importa el DDL EXACTO de tus models (ruta mantenida)
            from db.models.models import SCHEMA_SQL
        except ModuleNotFoundError as e:
            raise RuntimeError(
                "❌ No se encontró 'SCHEMA_SQL' en db.models.models. "
                "Asegúrate de que tu models.py define SCHEMA_SQL y que la ruta de import es correcta."
            ) from e

        try:
            with get_session() as conn:
                # executescript permite múltiples sentencias separadas por ';'
                conn.executescript(SCHEMA_SQL)
        except Exception as e:
            raise RuntimeError(f"❌ Error creando tablas SQLite: {e}") from e


@contextmanager
def get_session():
    """
    Context manager seguro para 'sesiones':
        with get_session() as db:
            db.execute("SQL ...", params)
        # commit/rollback automáticos
    """
    db = _connect()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
