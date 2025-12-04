"""Dashboard logic: fetch available tests (pruebas) from API."""
from __future__ import annotations
import flet as ft
from typing import Any, Dict, List

from ...API.crud import RestClient

# Base URL for MockAPI (same as login/register)
URL_API = "https://69069a11b1879c890ed7a77d.mockapi.io/"


class DashboardLogic:
    def __init__(self, page: ft.Page, user: dict | None = None):
        self.page = page
        self.user = user or {}
        self.api = RestClient(base_url=URL_API)
        self._exams_data: Dict[str, Dict[str, Any]] = {}  # Cache de datos completos de exámenes

    def _normalize_item(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Map arbitrary payload to UI-friendly keys.

        Expected by DashboardUI:
          - id
          - titulo
          - descripcion
          - full_data: datos completos del examen (para pasarlo al ExamView)
        """
        if not isinstance(raw, dict):
            return {"id": None, "titulo": "Prueba", "descripcion": "", "full_data": None}

        # Try common variants from the provided example
        titulo = (
            raw.get("titulo")
            or raw.get("exam_name")
            or raw.get("name")
            or "Prueba"
        )
        descripcion = (
            raw.get("descripcion")
            or raw.get("description")
            or raw.get("desc")
            or ""
        )
        return {
            "id": raw.get("id"),
            "titulo": titulo,
            "descripcion": descripcion,
            "full_data": raw,  # Guardar los datos completos
        }

    # Cargar dinamicamente las pruebas desde la API
    def cargaPruebas(self) -> List[Dict[str, Any]]:
        """Fetch list of exams/pruebas from API, trying common variants.

        Tries, in order: pruebas, exams, Exams, Pruebas.
        """
        items: List[Dict[str, Any]] = []

        for path in ("pruebas", "exams", "Exams", "Pruebas"):
            ok, data, status, err = self.api.get(path)
            if ok and isinstance(data, list):
                items = [self._normalize_item(d) for d in data]
                # Guardar también los datos completos en el objeto para acceso rápido
                self._exams_data = {item["id"]: item["full_data"] for item in items if item["id"]}
                break

        return items
    
    def get_exam_data(self, exam_id: str) -> Dict[str, Any] | None:
        """Obtiene los datos completos de un examen por su ID"""
        if hasattr(self, "_exams_data"):
            return self._exams_data.get(exam_id) or self._exams_data.get(str(exam_id))
        return None

    #Funcion para entrar a cada una de las pruebas cuando esten disponibles
    def on_nav_change(self, index: int):
        print(f"[DASH-LOGIC] Tab seleccionado: {index}")
