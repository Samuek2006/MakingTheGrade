import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================
# Cargar variables de entorno desde .env
# ============================================
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "marking_grade")

# ============================================
# Configuración de URLs de conexión
# ============================================
BASE_URL_NO_DB = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
DATABASE_URL   = f"{BASE_URL_NO_DB}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    echo=False,          # Cambia a True para ver los queries en consola
    future=True,
    pool_pre_ping=True,  # "autoping" para reciclar conexiones muertas
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
    expire_on_commit=False,  # 👈 evita DetachedInstanceError
)

Base = declarative_base()


def create_database_if_not_exists():
    """
    Crea la base de datos si no existe (útil al iniciar en XAMPP).
    """
    tmp_engine = create_engine(
        BASE_URL_NO_DB,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    dbname = DB_NAME.replace("`", "")  # evitar inyección en el nombre
    with tmp_engine.connect() as conn:
        conn.execute(
            text(f"CREATE DATABASE IF NOT EXISTS `{dbname}` "
                 "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        )
        conn.commit()


def init_db(create_all: bool = False):
    """
    Inicializa la base de datos:
        1) Crea la DB si no existe.
        2) Si create_all=True, crea todas las tablas definidas en models.py
    """
    try:
        create_database_if_not_exists()

        if create_all:
            from apps.db.models.models import (
                User, Question, QuestionOption, QuestionCorrect,
                Attempt, AttemptItem, ItemGrade
            )
            Base.metadata.create_all(bind=engine)

    except OperationalError as e:
        raise RuntimeError(
            "❌ No se pudo inicializar la base de datos. "
            "Verifica que MySQL/MariaDB de XAMPP esté corriendo, "
            "el puerto, usuario y contraseña."
        ) from e


@contextmanager
def get_session():
    """
    Context manager seguro para sesiones SQLAlchemy:
        with get_session() as db:
            db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
