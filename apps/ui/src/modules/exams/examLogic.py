# src/modules/exams/examLogic.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from ...API.crud import RestClient

# Base URL for MockAPI
URL_API = "https://69069a11b1879c890ed7a77d.mockapi.io/"


class ExamLogic:
    """
    Lógica para manejar exámenes/pruebas desde mockapi.
    Maneja el estado de la prueba, respuestas y validación.
    """
    
    def __init__(self, exam_id: str, exam_data: Optional[Dict[str, Any]] = None):
        self.exam_id = exam_id
        self.api = RestClient(base_url=URL_API)
        self.exam_data: Dict[str, Any] = {}
        self.questions: List[Dict[str, Any]] = []
        self.current_question_idx = 0
        self.selected_answer: Optional[str] = None
        self.user_answers: Dict[int, Dict[str, Any]] = {}  # {idx: {"answer": "a", "correct": True}}
        self.show_result = False  # Si True, muestra la respuesta correcta y si quedó bien
        self.total_correct = 0
        
        # Si se proporcionan datos directamente, usarlos
        if exam_data:
            self.exam_data = exam_data
            questions = exam_data.get("questions", []) or exam_data.get("preguntas", [])
            if questions and len(questions) > 0:
                self.questions = questions
    
    def load_exam(self) -> bool:
        """
        Carga el examen desde la API o usa los datos ya proporcionados.
        Si ya se proporcionaron datos en __init__, los usa directamente.
        Si no, intenta cargarlos desde la API.
        """
        # Si ya tenemos preguntas (se cargaron en __init__), retornar True
        if self.questions and len(self.questions) > 0:
            return True
        
        if not self.exam_id:
            return False
        
        # Si no tenemos datos, intentar cargar desde la API
        # Primero intentar obtener de la lista completa
        for endpoint in ["exams", "pruebas"]:
            ok, data_list, status, err = self.api.get(endpoint)
            
            if ok and isinstance(data_list, list):
                # Buscar el examen por ID en la lista
                for exam in data_list:
                    exam_id_str = str(exam.get("id", ""))
                    if exam_id_str == str(self.exam_id):
                        self.exam_data = exam
                        questions = exam.get("questions", []) or exam.get("preguntas", [])
                        if questions and len(questions) > 0:
                            self.questions = questions
                            return True
        
        # Fallback: intentar cargar directamente por ID (puede que funcione en algunos casos)
        for endpoint in ["exams", "pruebas"]:
            url = f"{endpoint}/{self.exam_id}"
            ok, data, status, err = self.api.get(url)
            
            if ok and isinstance(data, dict):
                self.exam_data = data
                # Normalizar las preguntas
                questions = data.get("questions", []) or data.get("preguntas", [])
                if questions and len(questions) > 0:
                    self.questions = questions
                    return True
        
        return False
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Obtiene la pregunta actual"""
        if 0 <= self.current_question_idx < len(self.questions):
            return self.questions[self.current_question_idx]
        return None
    
    def select_answer(self, option_key: str):
        """Selecciona una respuesta (solo si aún no se ha validado)"""
        if not self.show_result:
            self.selected_answer = option_key
    
    def validate_and_show_result(self) -> bool:
        """
        Valida la respuesta actual y muestra el resultado.
        Retorna True si se pudo validar (había una respuesta seleccionada).
        """
        if self.show_result:
            return True  # Ya está validada
        
        if not self.selected_answer:
            return False  # No hay respuesta seleccionada
        
        question = self.get_current_question()
        if not question:
            return False
        
        # Obtener la respuesta correcta
        correct_answer = question.get("correct", "")
        is_correct = str(self.selected_answer).lower() == str(correct_answer).lower()
        
        # Guardar la respuesta del usuario
        self.user_answers[self.current_question_idx] = {
            "answer": self.selected_answer,
            "correct": is_correct,
            "correct_answer": correct_answer
        }
        
        if is_correct:
            self.total_correct += 1
        
        # Mostrar resultado
        self.show_result = True
        return True
    
    def next_question(self) -> bool:
        """
        Avanza a la siguiente pregunta.
        Retorna True si hay más preguntas, False si es la última.
        """
        if self.current_question_idx < len(self.questions) - 1:
            self.current_question_idx += 1
            self.selected_answer = None
            self.show_result = False
            
            # Restaurar respuesta previa si existe
            if self.current_question_idx in self.user_answers:
                prev_answer = self.user_answers[self.current_question_idx]
                self.selected_answer = prev_answer.get("answer")
                self.show_result = prev_answer.get("validated", False)
            
            return True
        return False
    
    def previous_question(self) -> bool:
        """Retrocede a la pregunta anterior"""
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            self.show_result = False
            
            # Restaurar respuesta previa si existe
            if self.current_question_idx in self.user_answers:
                prev_answer = self.user_answers[self.current_question_idx]
                self.selected_answer = prev_answer.get("answer")
                self.show_result = prev_answer.get("validated", False)
            else:
                self.selected_answer = None
            
            return True
        return False
    
    def continue_after_result(self):
        """
        Continúa después de mostrar el resultado.
        Si hay más preguntas, avanza. Si no, retorna False.
        """
        if self.show_result:
            # Marcar como validada
            if self.current_question_idx in self.user_answers:
                self.user_answers[self.current_question_idx]["validated"] = True
            
            return self.next_question()
        return False
    
    def get_exam_info(self) -> Dict[str, Any]:
        """Obtiene información general del examen"""
        return {
            "id": self.exam_data.get("id"),
            "exam_name": self.exam_data.get("exam_name") or self.exam_data.get("titulo", ""),
            "subject": self.exam_data.get("subject") or self.exam_data.get("materia", ""),
            "description": self.exam_data.get("description") or self.exam_data.get("descripcion", ""),
            "total_points": self.exam_data.get("total_points") or self.exam_data.get("total_puntos", 0),
            "total_questions": len(self.questions)
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """Obtiene información del progreso"""
        total = len(self.questions)
        current = self.current_question_idx + 1
        answered = len(self.user_answers)
        
        return {
            "current": current,
            "total": total,
            "answered": answered,
            "correct": self.total_correct,
            "progress_percent": (current / total * 100) if total > 0 else 0
        }
    
    def is_last_question(self) -> bool:
        """Verifica si es la última pregunta"""
        return self.current_question_idx >= len(self.questions) - 1
    
    def get_final_score(self) -> Dict[str, Any]:
        """Calcula el puntaje final"""
        total = len(self.questions)
        correct = self.total_correct
        answered = len(self.user_answers)
        incorrect = answered - correct
        unanswered = total - answered
        
        score_percent = (correct / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "unanswered": unanswered,
            "score_percent": score_percent,
            "total_points": self.exam_data.get("total_points", 0),
            "earned_points": (correct / total * self.exam_data.get("total_points", 0)) if total > 0 else 0
        }

