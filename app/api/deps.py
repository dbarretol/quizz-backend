"""
Dependencias para los endpoints de la API.
"""
from functools import lru_cache
from app.services.firestore_service import FirestoreService
from app.services.gemini_service import GeminiService


@lru_cache()
def get_firestore_service() -> FirestoreService:
    """
    Obtiene una instancia del servicio de Firestore.
    Utiliza cache para reutilizar la misma instancia.
    
    Returns:
        FirestoreService: Instancia del servicio
    """
    return FirestoreService()


@lru_cache() 
def get_gemini_service() -> GeminiService:
    """
    Obtiene una instancia del servicio de Gemini.
    Utiliza cache para reutilizar la misma instancia.
    
    Returns:
        GeminiService: Instancia del servicio
    """
    return GeminiService()