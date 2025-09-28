"""
Endpoints para generar explicaciones de preguntas.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends

from app.api.deps import get_gemini_service
from app.services.gemini_service import GeminiService
from app.models.schemas import ExplanationRequest, ExplanationResponse, ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=ExplanationResponse)
async def generate_explanation(
    request: ExplanationRequest,
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> ExplanationResponse:
    """
    Genera una explicación detallada para una pregunta usando IA.
    
    Args:
        request: Datos de la solicitud con el texto de la pregunta
        gemini_service: Servicio de Gemini inyectado
        
    Returns:
        ExplanationResponse: Explicación generada en formato Markdown
        
    Example:
        POST /api/v1/explanations/generate
        {
            "question_text": "¿Cuál es la capital de Francia?"
        }
    """
    logger.info(f"Generando explicación para: {request.question_text[:50]}...")
    
    explanation = await gemini_service.generate_explanation(request.question_text)
    
    return ExplanationResponse(explanation=explanation)


@router.get("/test", response_model=ApiResponse)
async def test_gemini_connection(
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> ApiResponse:
    """
    Prueba la conectividad con el servicio de Gemini.
    
    Args:
        gemini_service: Servicio de Gemini inyectado
        
    Returns:
        ApiResponse: Resultado de la prueba de conexión
        
    Example:
        GET /api/v1/explanations/test
    """
    logger.info("Probando conexión con Gemini")
    
    result = await gemini_service.test_connection()
    
    return ApiResponse(
        status=result["status"],
        message=result["message"],
        data=result if result["status"] == "success" else None
    )