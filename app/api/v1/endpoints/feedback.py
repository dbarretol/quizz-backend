"""
Endpoints para generar feedback personalizado.
"""
import logging
from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service
from app.services.gemini_service import GeminiService
from app.models.schemas import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=FeedbackResponse)
async def generate_personalized_feedback(
    request: FeedbackRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> FeedbackResponse:
    """
    Genera feedback educativo personalizado basado en las respuestas del usuario.
    
    El feedback se genera como una separata informativa que ayuda al estudiante
    a repasar los conceptos relacionados con las preguntas que respondió incorrectamente.
    
    Args:
        request: Datos del quiz (preguntas y respuestas del usuario)
        gemini_service: Servicio de Gemini inyectado
        
    Returns:
        FeedbackResponse: Feedback personalizado en formato Markdown
        
    Example:
        POST /api/v1/feedback/generate
        {
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
    """
    incorrect_count = sum(
        1 for i, q in enumerate(request.questions)
        if request.user_attempt.answers[i] != q.correct_answer
    )
    
    logger.info(f"Generando feedback - Preguntas incorrectas: {incorrect_count}/{request.user_attempt.total_questions}")
    
    feedback = await gemini_service.generate_feedback(
        request.questions, 
        request.user_attempt
    )
    
    return FeedbackResponse(feedback=feedback)