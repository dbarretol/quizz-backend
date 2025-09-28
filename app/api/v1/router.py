"""
Router principal de la API v1.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import questions, explanations, feedback

# Router principal de la API
api_router = APIRouter()

# Incluir todos los endpoints
api_router.include_router(
    questions.router,
    prefix="/questions",
    tags=["Questions"]
)

api_router.include_router(
    explanations.router,
    prefix="/explanations", 
    tags=["Explanations"]
)

api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Feedback"]
)