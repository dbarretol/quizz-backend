"""
Aplicación principal de FastAPI para el servicio de Quiz.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.config.settings import settings
from app.api.v1.router import api_router


# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    """
    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.version}")
    logger.info(f"Entorno: {settings.environment}")
    
    # Validar configuración crítica
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY no configurada")
        raise ValueError("GEMINI_API_KEY es requerida")
    
    logger.info("Aplicación iniciada correctamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI.
    
    Returns:
        FastAPI: Instancia de la aplicación configurada
    """
    # Crear aplicación
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Endpoint de salud básico
    @app.get("/", tags=["Health"])
    async def health_check():
        """Endpoint de verificación de salud."""
        return {
            "message": f"Welcome to {settings.app_name}!",
            "version": settings.version,
            "status": "healthy"
        }
    
    return app


# Crear instancia de la aplicación
app = create_app()