"""
Endpoints para manejo de preguntas.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.deps import get_firestore_service
from app.services.firestore_service import FirestoreService
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Configurar plantillas
templates = Jinja2Templates(directory="app/templates")


@router.get("/test", response_class=HTMLResponse)
async def serve_test_page(request: Request):
    """
    Sirve la página de prueba HTML.
    
    Args:
        request: Request object de FastAPI
        
    Returns:
        HTMLResponse: Página HTML de prueba
    """
    return templates.TemplateResponse("template.html", {"request": request})


@router.get("/{question_id}")
async def get_question_by_id(
    question_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service)
) -> Dict[str, Any]:
    """
    Obtiene una pregunta específica por su ID.
    
    Args:
        question_id: ID único de la pregunta
        firestore_service: Servicio de Firestore inyectado
        
    Returns:
        dict: Datos de la pregunta
        
    Example:
        GET /api/v1/questions/5
    """
    logger.info(f"Solicitando pregunta con ID: {question_id}")
    return await firestore_service.get_question_by_id(question_id)


@router.get("/")
async def get_random_questions(
    count: int = Query(
        5, 
        ge=1, 
        le=settings.max_questions_per_request,
        description="Número de preguntas aleatorias a obtener"
    ),
    subject: Optional[str] = Query(
        None,
        description="Filtro opcional por materia/tema"
    ),
    firestore_service: FirestoreService = Depends(get_firestore_service)
) -> List[Dict[str, Any]]:
    """
    Obtiene preguntas aleatorias de la base de datos.
    
    Args:
        count: Número de preguntas a obtener (1-20)
        subject: Filtro opcional por materia
        firestore_service: Servicio de Firestore inyectado
        
    Returns:
        list: Lista de preguntas aleatorias
        
    Example:
        GET /api/v1/questions/?count=3&subject=Historia
    """
    logger.info(f"Solicitando {count} preguntas aleatorias" + 
               (f" de la materia: {subject}" if subject else ""))
    
    return await firestore_service.get_random_questions(count, subject)


@router.get("/subjects/available")
async def get_available_subjects(
    firestore_service: FirestoreService = Depends(get_firestore_service)
) -> Dict[str, List[str]]:
    """
    Obtiene la lista de materias/temas disponibles.
    
    Args:
        firestore_service: Servicio de Firestore inyectado
        
    Returns:
        dict: Lista de materias disponibles
        
    Example:
        GET /api/v1/questions/subjects/available
    """
    logger.info("Solicitando materias disponibles")
    subjects = await firestore_service.get_available_subjects()
    
    return {"subjects": subjects}


@router.get("/count/total")
async def get_questions_count(
    subject: Optional[str] = Query(
        None,
        description="Filtro opcional por materia para el conteo"
    ),
    firestore_service: FirestoreService = Depends(get_firestore_service)
) -> Dict[str, Any]:
    """
    Obtiene el número total de preguntas disponibles.
    
    Args:
        subject: Filtro opcional por materia
        firestore_service: Servicio de Firestore inyectado
        
    Returns:
        dict: Información del conteo
        
    Example:
        GET /api/v1/questions/count/total?subject=Geografia
    """
    logger.info("Solicitando conteo de preguntas" + 
               (f" para la materia: {subject}" if subject else ""))
    
    count = await firestore_service.get_questions_count(subject)
    
    return {
        "total_questions": count,
        "subject": subject,
        "filtered": subject is not None
    }