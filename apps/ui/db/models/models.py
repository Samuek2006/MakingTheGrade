# models.py — versión SQLite sin SQLAlchemy (DDL + enums)
import enum

# =========================
# Enums (se mantienen igual)
# =========================
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


# ============================================================
# SCHEMA_SQL: DDL para crear TODAS las tablas en SQLite
# (equivalente a tus modelos ORM originales)
# ============================================================
SCHEMA_SQL = """
-- ============================================
-- USERS
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacion  TEXT UNIQUE NOT NULL,
    nombre          TEXT NOT NULL,
    apellido        TEXT NOT NULL,
    telefono        TEXT,
    rol             TEXT NOT NULL CHECK (rol IN ('admin','qualifier','student')),
    estado          TEXT,
    username        TEXT UNIQUE,
    password_hash   TEXT,
    direccion       TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ============================================
-- QUESTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS questions (
    id        TEXT PRIMARY KEY,  -- ej: Q1, PC1, PE1
    qtype     TEXT NOT NULL CHECK (qtype IN ('cerrada','corta','ensayo')),
    texto     TEXT NOT NULL,
    puntos    INTEGER,
    tema      TEXT,
    titulo    TEXT,
    autor     TEXT,
    estado    TEXT
);

-- ============================================
-- QUESTION_OPTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS question_options (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id  TEXT NOT NULL,
    opt_key      TEXT NOT NULL,
    opt_text     TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE (question_id, opt_key)  -- uq_q_opt
);

-- ============================================
-- QUESTION_CORRECT
-- ============================================
CREATE TABLE IF NOT EXISTS question_correct (
    question_id  TEXT PRIMARY KEY,
    correct_key  TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- ============================================
-- ATTEMPTS
-- ============================================
CREATE TABLE IF NOT EXISTS attempts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    section       TEXT NOT NULL CHECK (section IN ('Cerradas','Cortas','Ensayo')),
    attempted_at  TEXT NOT NULL,           -- ISO8601 string
    total_points  INTEGER,
    score_pct     REAL,                    -- DECIMAL(5,2) -> REAL
    graded        INTEGER DEFAULT 0,       -- 0/1
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- ATTEMPT_ITEMS
-- ============================================
CREATE TABLE IF NOT EXISTS attempt_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id   INTEGER NOT NULL,
    question_id  TEXT NOT NULL,
    user_answer  TEXT,
    is_correct   INTEGER,                  -- 0/1/NULL
    points       INTEGER,
    FOREIGN KEY (attempt_id) REFERENCES attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- ============================================
-- ITEM_GRADES
-- ============================================
CREATE TABLE IF NOT EXISTS item_grades (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id   INTEGER NOT NULL,
    question_id  TEXT NOT NULL,
    grade        REAL NOT NULL,            -- DECIMAL(6,2) -> REAL
    graded_at    TEXT NOT NULL,            -- ISO8601 string
    FOREIGN KEY (attempt_id) REFERENCES attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- ============================================
-- PRUEBAS
-- ============================================
CREATE TABLE IF NOT EXISTS pruebas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo        TEXT NOT NULL,
    descripcion   TEXT,
    categoria     TEXT,
    estado        TEXT NOT NULL DEFAULT 'Activo',
    duracion_seg  INTEGER,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================
-- PREGUNTAS (de PRUEBAS)
-- ============================================
CREATE TABLE IF NOT EXISTS preguntas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    prueba_id     INTEGER NOT NULL,
    enunciado     TEXT NOT NULL,
    secuencia     TEXT,
    opciones_json TEXT,
    correcta      TEXT,
    orden         INTEGER,
    estado        TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (prueba_id) REFERENCES pruebas(id) ON DELETE CASCADE
);
"""
