"""
Modelos Pydantic para validación de datos.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ExplanationRequest(BaseModel):
    """Modelo para solicitud de explicación."""
    question_text: str = Field(..., min_length=1, description="Texto de la pregunta a explicar")
    
    class Config:
        schema_extra = {
            "example": {
                "question_text": "¿Cuál es la capital de Francia?"
            }
        }


class ExplanationResponse(BaseModel):
    """Modelo para respuesta de explicación."""
    explanation: str = Field(..., description="Explicación generada por IA")
    
    class Config:
        schema_extra = {
            "example": {
                "explanation": "París es la capital de Francia..."
            }
        }


class Question(BaseModel):
    """Modelo para una pregunta del quiz."""
    id: int = Field(..., description="ID único de la pregunta")
    question: str = Field(..., description="Texto de la pregunta")
    options: List[str] = Field(..., min_items=2, description="Lista de opciones de respuesta")
    correct_answer: int = Field(..., ge=0, description="Índice de la respuesta correcta")
    subject: Optional[str] = Field(None, description="Materia o tema de la pregunta")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "question": "¿Cuál es la capital de Francia?",
                "options": ["Londres", "París", "Madrid", "Roma"],
                "correct_answer": 1,
                "subject": "Geografía"
            }
        }


class UserAttempt(BaseModel):
    """Modelo para un intento de respuesta del usuario."""
    score: int = Field(..., ge=0, description="Puntuación obtenida")
    total_questions: int = Field(..., gt=0, description="Número total de preguntas")
    answers: List[int] = Field(..., description="Lista de respuestas del usuario (índices)")
    
    class Config:
        schema_extra = {
            "example": {
                "score": 3,
                "total_questions": 5,
                "answers": [1, 0, 2, 1, 3]
            }
        }


class FeedbackRequest(BaseModel):
    """Modelo para solicitud de feedback personalizado."""
    questions: List[Question] = Field(..., min_items=1, description="Lista de preguntas del quiz")
    user_attempt: UserAttempt = Field(..., description="Intento del usuario")
    
    class Config:
        schema_extra = {
            "example": {
                "questions": [
                    {
                        "id": 1,
                        "question": "¿Cuál es la capital de Francia?",
                        "options": ["Londres", "París", "Madrid", "Roma"],
                        "correct_answer": 1
                    }
                ],
                "user_attempt": {
                    "score": 0,
                    "total_questions": 1,
                    "answers": [0]
                }
            }
        }


class FeedbackResponse(BaseModel):
    """Modelo para respuesta de feedback."""
    feedback: str = Field(..., description="Feedback personalizado generado por IA")
    
    class Config:
        schema_extra = {
            "example": {
                "feedback": "## Repaso de Geografía Europea\n\n### Francia y sus características..."
            }
        }


class ApiResponse(BaseModel):
    """Modelo genérico para respuestas de la API."""
    status: str = Field(..., description="Estado de la respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[dict] = Field(None, description="Datos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Operación completada exitosamente",
                "data": {}
            }
        }