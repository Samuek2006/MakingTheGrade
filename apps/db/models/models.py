# models.py
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Enum, DateTime, DECIMAL, TIMESTAMP,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import enum

class RolEnum(enum.Enum):
    admin = "admin"
    qualifier = "qualifier"
    student = "student"

class QTypeEnum(enum.Enum):
    cerrada = "cerrada"
    corta = "corta"
    ensayo = "ensayo"

class SectionEnum(enum.Enum):
    Cerradas = "Cerradas"
    Cortas = "Cortas"
    Ensayo = "Ensayo"

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    identificacion = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(30))
    rol = Column(Enum(RolEnum), nullable=False)
    estado = Column(String(50))
    username = Column(String(100), unique=True)
    password_hash = Column(String(255))
    direccion = Column(String(255))
    created_at = Column(TIMESTAMP)

    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(String(50), primary_key=True)  # ej: Q1, PC1, PE1
    qtype = Column(Enum(QTypeEnum), nullable=False)
    texto = Column(Text, nullable=False)
    puntos = Column(Integer)
    tema = Column(String(120))
    titulo = Column(String(255))
    autor = Column(String(255))
    estado = Column(String(50))

    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    correct = relationship("QuestionCorrect", back_populates="question", uselist=False, cascade="all, delete-orphan")

class QuestionOption(Base):
    __tablename__ = "question_options"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    opt_key = Column(String(10), nullable=False)
    opt_text = Column(Text, nullable=False)

    question = relationship("Question", back_populates="options")
    __table_args__ = (UniqueConstraint("question_id", "opt_key", name="uq_q_opt"),)

class QuestionCorrect(Base):
    __tablename__ = "question_correct"
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    correct_key = Column(String(20), nullable=False)

    question = relationship("Question", back_populates="correct")

class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    section = Column(Enum(SectionEnum), nullable=False)
    attempted_at = Column(DateTime, nullable=False)
    total_points = Column(Integer)
    score_pct = Column(DECIMAL(5,2))
    graded = Column(Integer, default=0)

    user = relationship("User", back_populates="attempts")
    items = relationship("AttemptItem", back_populates="attempt", cascade="all, delete-orphan")
    item_grades = relationship("ItemGrade", back_populates="attempt", cascade="all, delete-orphan")

class AttemptItem(Base):
    __tablename__ = "attempt_items"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(Text)
    is_correct = Column(Integer)   # 1/0/NULL
    points = Column(Integer)

    attempt = relationship("Attempt", back_populates="items")
    question = relationship("Question")

class ItemGrade(Base):
    __tablename__ = "item_grades"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    attempt_id = Column(BigInteger, ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(50), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    grade = Column(DECIMAL(6,2), nullable=False)
    graded_at = Column(DateTime, nullable=False)

    attempt = relationship("Attempt", back_populates="item_grades")
    question = relationship("Question")


# ──────────────────────────────────────────────────────────────────────────────
# PRUEBAS
# ──────────────────────────────────────────────────────────────────────────────

class Prueba(Base):
    __tablename__ = "pruebas"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # Título de la prueba (si prefieres "nombre", cambia aquí y en el CRUD)
    titulo = Column(String(255), nullable=False)

    # Descripción corta / subtítulo
    descripcion = Column(Text, nullable=True)

    # Categoría opcional (ej: "Lógico", "Numérico"...)
    categoria = Column(String(100), nullable=True)

    # Estado (usa "Activo" / "Inactivo" según tu app)
    estado = Column(String(50), nullable=False, default="Activo")

    # Duración total en segundos (si prefieres minutos, crea 'duracion_min' en su lugar)
    duracion_seg = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relación: una prueba tiene muchas preguntas
    preguntas = relationship(
        "Pregunta",
        back_populates="prueba",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # FK a pruebas.id
    prueba_id = Column(
        BigInteger,
        ForeignKey("pruebas.id", ondelete="CASCADE"),
        nullable=False
    )

    # Texto de la pregunta
    enunciado = Column(Text, nullable=False)

    # Campo opcional para secuencias (ej. "2, 4, 8, 16, ...")
    secuencia = Column(Text, nullable=True)

    # Opciones serializadas como JSON (ej. '["A","B","C","D"]')
    # Si prefieres guardarlas en filas separadas, cambia tu CRUD.
    opciones_json = Column(Text, nullable=True)

    # Respuesta correcta (coincide con alguna opción o texto libre si es corta)
    correcta = Column(String(255), nullable=True)

    # Orden de aparición dentro de la prueba
    orden = Column(Integer, nullable=True)

    # Estado (opcional)
    estado = Column(String(50), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relaciones
    prueba = relationship("Prueba", back_populates="preguntas")