# src/modules/pruebas/prueba_logic.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import timedelta
import asyncio
import json
from ast import literal_eval
from ...API.crud import RestClient

# Base URL for MockAPI
URL_API = "https://69069a11b1879c890ed7a77d.mockapi.io/"

@dataclass
class OptionData:
    text: str
    image: Optional[str] = None

@dataclass
class ViewModel:
    titulo: str
    total: int
    idx: int
    enunciado: str
    secuencia: Optional[str]
    opciones: List[OptionData]
    seleccion_actual: Optional[str]
    validada: bool
    aciertos: int
    tiempo_mmss: str
    progreso_val: float
    progreso_txt: str

class PruebaLogic:
    """
    Se encarga de:
        - Cargar datos de prueba y normalizarlos
        - Llevar estado (índice, selección, validadas, aciertos, tiempo)
        - Validar respuestas y calcular puntaje
        - Guardar intento al finalizar
        - Exponer un ViewModel para que la UI se repinte
    """
    def __init__(self, prueba_id: int, default_duracion_seg: int = 9*60 + 30):
        self.prueba_id = prueba_id
        self.api = RestClient(base_url=URL_API)
        self.data: Dict[str, Any] = {}
        self.questions: List[Dict[str, Any]] = []
        self.idx = 0
        self.seleccion: Optional[str] = None
        self.user_answers: Dict[int, Dict[str, Any]] = {}
        self.validadas: set[int] = set()
        self.aciertos = 0
        self.total_seconds = default_duracion_seg
        self.remaining = default_duracion_seg
        self._timer_stop = False

    # ---------- Carga ----------
    def cargar(self) -> bool:
        """Fetch the test and questions from the API and normalize fields.

        Strategy:
          1) GET pruebas/{id} expecting embedded "preguntas" (if present).
          2) If not embedded, GET pruebas/{id}/preguntas and attach.
        """
        ok, payload, status, err = self.api.get(f"pruebas/{self.prueba_id}")
        if not ok or not isinstance(payload, dict):
            return False

        data: Dict[str, Any] = payload or {}

        if not data.get("preguntas"):
            ok_p, preguntas, _st_p, _err_p = self.api.get(f"pruebas/{self.prueba_id}/preguntas")
            if ok_p and isinstance(preguntas, list):
                data["preguntas"] = preguntas

        self.data = data
        try:
            self.total_seconds = int(data.get("duracion_seg") or self.total_seconds)
        except Exception:
            pass
        self.remaining = self.total_seconds

        qs: List[Dict[str, Any]] = []
        for p in data.get("preguntas", []) or []:
            if not isinstance(p, dict):
                continue
            qs.append(
                {
                    "titulo": data.get("titulo", ""),
                    "enunciado": p.get("enunciado", ""),
                    "secuencia": p.get("secuencia"),
                    "opciones": p.get("opciones", []) or [],
                    "correcta": p.get("correcta"),
                }
            )
        self.questions = qs
        return True

    # ---------- Helpers ----------
    def _coerce_to_dict(self, opt: Any) -> OptionData:
        if isinstance(opt, dict):
            return OptionData(text=str(opt.get("text", "")).strip(), image=(opt.get("image") or None))
        s = str(opt).strip()
        if s.startswith("{") or s.startswith("["):
            # intenta JSON
            try:
                d = json.loads(s.replace("'", '"'))
                if isinstance(d, dict):
                    return OptionData(text=str(d.get("text", "")).strip(), image=(d.get("image") or None))
            except Exception:
                # intenta repr Python
                try:
                    d = literal_eval(s)
                    if isinstance(d, dict):
                        return OptionData(text=str(d.get("text", "")).strip(), image=(d.get("image") or None))
                except Exception:
                    pass
        return OptionData(text=s, image=None)

    def _opt_text(self, opt: Any) -> str:
        return self._coerce_to_dict(opt).text

    def _es_correcta(self, q: Dict[str, Any], value_text: str) -> bool:
        c = q.get("correcta")
        if c is None:
            return False
        if isinstance(c, int):
            try:
                return self._opt_text((q.get("opciones") or [])[c]) == value_text
            except Exception:
                return False
        return str(c) == value_text

    def _mmss(self) -> str:
        t = str(timedelta(seconds=self.remaining))
        return t.split(":")[1] + ":" + t.split(":")[2].zfill(2)

    # ---------- Navegación & selección ----------
    def seleccionar(self, value_text: str) -> None:
        if self.idx in self.validadas:
            return
        self.seleccion = value_text

    def validar_actual(self) -> bool:
        """Valida la pregunta actual; devuelve True si se pudo validar (había selección)."""
        if self.idx in self.validadas:
            return True  # ya estaba validada

        q = self.questions[self.idx]
        if self.seleccion is None:
            return False

        ok = self._es_correcta(q, self.seleccion)
        anterior = self.user_answers.get(self.idx)
        if anterior is None:
            self.user_answers[self.idx] = {"seleccion": self.seleccion, "correcta": ok}
            if ok:
                self.aciertos += 1
        else:
            if ok != bool(anterior.get("correcta")):
                self.aciertos += 1 if ok else -1
            anterior["seleccion"] = self.seleccion
            anterior["correcta"] = ok

        self.validadas.add(self.idx)
        return True

    def siguiente(self) -> bool:
        """Avanza si hay más preguntas. Devuelve False si ya estaba en la última."""
        if self.idx < len(self.questions) - 1:
            self.idx += 1
            self.seleccion = self.user_answers.get(self.idx, {}).get("seleccion")
            return True
        return False

    def anterior(self) -> bool:
        if self.idx > 0:
            self.idx -= 1
            self.seleccion = self.user_answers.get(self.idx, {}).get("seleccion")
            return True
        return False

    # ---------- Finalización ----------
    def finalizar(self, motivo: str = "finalizado") -> Dict[str, Any]:
        """Calcula resumen y persiste intento."""
        self._timer_stop = True
        total = len(self.questions)
        contestadas = len(self.user_answers)
        correctas = self.aciertos
        pendientes = total - contestadas
        score_pct = 100.0 * correctas / total if total else 0.0

        # Save attempt to API
        resp_payload = {
            "prueba_id": self.prueba_id,
            "total_preguntas": total,
            "correctas": correctas,
            "incorrectas": contestadas - correctas,
            "pendientes": pendientes,
            "puntaje": score_pct,
            "motivo": motivo,
            "respuestas": [
                {"pregunta_idx": i, "seleccion": d.get("seleccion"), "correcta": bool(d.get("correcta"))}
                for i, d in sorted(self.user_answers.items(), key=lambda t: t[0])
            ],
        }

        try:
            self._guardar_intento(resp_payload)
        except Exception as ex:
            return {
                "error": str(ex),
                "resumen": {
                    "correctas": correctas,
                    "incorrectas": contestadas - correctas,
                    "pendientes": pendientes,
                    "puntaje": score_pct,
                    "motivo": motivo,
                },
            }

        return {"resumen": {
            "correctas": correctas, "incorrectas": contestadas - correctas,
            "pendientes": pendientes, "puntaje": score_pct, "motivo": motivo
        }}

    # ---------- Persistencia API ----------
    def _guardar_intento(self, payload: Dict[str, Any]) -> Tuple[bool, Any]:
        """Try POST to 'intentos' then fallback to 'results'."""
        ok, data, status, err = self.api.post("intentos", json=payload)
        if ok:
            return True, data
        ok2, data2, status2, err2 = self.api.post("results", json=payload)
        if ok2:
            return True, data2
        raise RuntimeError(f"No se pudo guardar intento: HTTP {status} {err or ''} | alt HTTP {status2} {err2 or ''}")

    # ---------- Timer ----------
    async def countdown(self, on_tick: Optional[Callable[[], None]] = None,
                        on_timeout: Optional[Callable[[], None]] = None):
        self._timer_stop = False
        while self.remaining > 0 and not self._timer_stop:
            await asyncio.sleep(1)
            self.remaining -= 1
            if on_tick:
                on_tick()
        if self.remaining <= 0 and not self._timer_stop:
            if on_timeout:
                on_timeout()

    def stop_timer(self):
        self._timer_stop = True

    # ---------- ViewModel ----------
    def view(self) -> ViewModel:
        if not self.questions:
            return ViewModel(
                titulo=self.data.get("titulo", ""),
                total=0, idx=0, enunciado="", secuencia=None, opciones=[],
                seleccion_actual=None, validada=False, aciertos=0,
                tiempo_mmss=self._mmss(), progreso_val=0.0, progreso_txt="0/0"
            )

        q = self.questions[self.idx]
        opciones = [self._coerce_to_dict(o) for o in (q.get("opciones") or [])]
        total = len(self.questions)
        return ViewModel(
            titulo=self.data.get("titulo", ""),
            total=total,
            idx=self.idx,
            enunciado=q.get("enunciado") or "",
            secuencia=q.get("secuencia"),
            opciones=opciones,
            seleccion_actual=self.user_answers.get(self.idx, {}).get("seleccion", self.seleccion),
            validada=(self.idx in self.validadas),
            aciertos=self.aciertos,
            tiempo_mmss=self._mmss(),
            progreso_val=(self.idx + 1) / total if total else 0.0,
            progreso_txt=f"Pregunta {self.idx + 1} de {total}",
        )
