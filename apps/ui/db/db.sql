-- ─────────────────────────────────────────────────────────────
-- 1️⃣ CREACIÓN DE BASE DE DATOS
-- ─────────────────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS marking_grade
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE marking_grade;

-- ─────────────────────────────────────────────────────────────
-- 2️⃣ TABLA DE USUARIOS (LOGIN)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    identificacion VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    rol ENUM('admin','qualifier','student') NOT NULL,
    estado VARCHAR(50),
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    direccion VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────
-- 3️⃣ TABLA DE PRUEBAS (Dashboard y Panel)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pruebas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT NULL,
    categoria VARCHAR(100) NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'Activo',
    duracion_seg INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- 4️⃣ PREGUNTAS DE UNA PRUEBA (con imágenes y opciones JSON)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preguntas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    prueba_id BIGINT UNSIGNED NOT NULL,
    enunciado TEXT NOT NULL,
    secuencia TEXT NULL,
    imagen_url TEXT NULL,
    opciones_json JSON NULL,
    correcta VARCHAR(255) NULL,
    orden INT NULL,
    estado VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_preguntas_prueba
        FOREIGN KEY (prueba_id) REFERENCES pruebas(id) ON DELETE CASCADE,
    INDEX idx_preguntas_prueba (prueba_id),
    INDEX idx_preguntas_orden (orden)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- 5️⃣ BANCO DE PREGUNTAS (compatibilidad con sistema previo)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questions (
    id VARCHAR(50) PRIMARY KEY,
    qtype ENUM('cerrada','corta','ensayo') NOT NULL,
    texto TEXT NOT NULL,
    puntos INT NULL,
    tema VARCHAR(120) NULL,
    titulo VARCHAR(255) NULL,
    autor VARCHAR(255) NULL,
    estado VARCHAR(50) NULL
) ENGINE=InnoDB;

ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS imagen_url TEXT NULL;

-- ─────────────────────────────────────────────────────────────
-- 6️⃣ OPCIONES DE PREGUNTAS CERRADAS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS question_options (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    question_id VARCHAR(50) NOT NULL,
    opt_key VARCHAR(10) NOT NULL,
    opt_text TEXT NOT NULL,
    UNIQUE KEY uq_q_opt (question_id, opt_key),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

ALTER TABLE question_options
    UMN IF NOT EXISTS opt_image_url TEXT NULL;

-- ─────────────────────────────────────────────────────────────
-- 7️⃣ RESPUESTA CORRECTA
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS question_correct (
    question_id VARCHAR(50) PRIMARY KEY,
    correct_key VARCHAR(20) NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- 8️⃣ INTENTOS / CALIFICACIONES
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attempts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    section ENUM('Cerradas','Cortas','Ensayo') NOT NULL,
    attempted_at DATETIME NOT NULL,
    total_points INT NULL,
    score_pct DECIMAL(5,2) NULL,
    graded TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attempt_items (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    attempt_id BIGINT UNSIGNED NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    user_answer TEXT NULL,
    is_correct TINYINT(1) NULL,
    points INT NULL,
    FOREIGN KEY (attempt_id) REFERENCES attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

ALTER TABLE attempt_items
    ADD COLUMN IF NOT EXISTS user_answer_image_url TEXT NULL,
    ADD COLUMN IF NOT EXISTS user_answer_json JSON NULL;

-- ─────────────────────────────────────────────────────────────
-- 9️⃣ INTENTOS DE PRUEBAS (Panel de control)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS prueba_intentos (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    prueba_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NULL,
    motivo VARCHAR(100) NULL,
    total_preguntas INT NOT NULL,
    correctas INT NOT NULL,
    score_pct DECIMAL(5,2) NOT NULL DEFAULT 0,
    finished_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prueba_intentos_prueba (prueba_id),
    INDEX idx_prueba_intentos_user (user_id),
    CONSTRAINT fk_prueba_intentos_prueba
        FOREIGN KEY (prueba_id) REFERENCES pruebas(id) ON DELETE CASCADE,
    CONSTRAINT fk_prueba_intentos_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────
-- 🔟 RESPUESTAS INDIVIDUALES POR INTENTO
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS prueba_respuestas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    intento_id BIGINT UNSIGNED NOT NULL,
    pregunta_idx INT NOT NULL,
    seleccion TEXT NOT NULL,
    correcta TINYINT(1) NOT NULL,
    INDEX idx_prueba_respuestas_intento (intento_id),
    CONSTRAINT fk_prueba_respuestas_intento
        FOREIGN KEY (intento_id) REFERENCES prueba_intentos(id) ON DELETE CASCADE
) ENGINE=InnoDB;
