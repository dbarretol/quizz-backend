"""
Configuración centralizada de la aplicación.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # API Configuration
    app_name: str = "Quiz Service API"
    version: str = "1.0.0"
    description: str = "API service for quiz management with AI-powered explanations"
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    
    # Gemini Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = "gemini-2.5-flash"
    
    # Firestore Configuration
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-key.json")
    
    # API Limits
    max_questions_per_request: int = 20
    max_explanation_tokens: int = 1000
    max_feedback_tokens: int = 1500
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __post_init__(self):
        """Validaciones post-inicialización."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY es requerida")
        
        # Configurar credentials de Google Cloud
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_application_credentials


# Instancia global de configuración
settings = Settings()