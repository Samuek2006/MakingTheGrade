"""
Validador sencillo de variables de entorno para la app Flet.

Uso:
  python scripts/check_env.py

Valida la presencia de .env (opcional) y muestra los valores
relevantes que la app usa en tiempo de ejecución.
"""
from __future__ import annotations
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"

    if load_dotenv:
        # Carga .env si existe (no es obligatorio para Android)
        load_dotenv(env_path if env_path.exists() else None)

    print("— Variables de entorno —")
    print(f".env encontrado: {'sí' if env_path.exists() else 'no'}  → {env_path}")

    app_env = os.getenv("APP_ENV", "dev")
    sqlite_db_path = os.getenv("SQLITE_DB_PATH")

    # Variables legacy (no requeridas actualmente; se usan defaults)
    db_host = os.getenv("DB_HOST", "192.168.137.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "tester")
    db_name = os.getenv("DB_NAME", "marking_grade")

    print(f"APP_ENV:            {app_env}")
    print(f"SQLITE_DB_PATH:     {sqlite_db_path or '(no definido → se usa Home/AppSandbox)'}")
    print("— Legacy/MySQL (opcional, no requerido) —")
    print(f"DB_HOST:            {db_host}")
    print(f"DB_PORT:            {db_port}")
    print(f"DB_USER:            {db_user}")
    print(f"DB_NAME:            {db_name}")

    # Reglas: actualmente no exigimos .env; el proyecto funciona con SQLite
    # en el sandbox de la app (Android/desktop) usando defaults.
    print("\nEstado: OK — La app puede ejecutarse sin .env (SQLite).\n"
          "Para personalizar ruta de la DB usa SQLITE_DB_PATH en .env.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

