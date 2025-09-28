"""
Excepciones personalizadas para la aplicación.
"""
from fastapi import HTTPException
from typing import Optional, Dict, Any


class QuizServiceException(Exception):
    """Excepción base para el servicio de quiz."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class FirestoreException(QuizServiceException):
    """Excepción para errores de Firestore."""
    pass


class GeminiException(QuizServiceException):
    """Excepción para errores de Gemini."""
    pass


class ValidationException(QuizServiceException):
    """Excepción para errores de validación."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Crea una HTTPException con formato estándar.
    
    Args:
        status_code: Código de estado HTTP
        message: Mensaje de error
        details: Detalles adicionales del error
        
    Returns:
        HTTPException configurada
    """
    detail = {"message": message}
    if details:
        detail["details"] = details
    
    return HTTPException(status_code=status_code, detail=detail)