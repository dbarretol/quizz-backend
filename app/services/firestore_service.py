"""
Servicio para interactuar con Firestore.
"""
import logging
import random
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError

from app.core.exceptions import FirestoreException, create_http_exception
from app.config.settings import settings

logger = logging.getLogger(__name__)


class FirestoreService:
    """Servicio para operaciones con Firestore."""
    
    def __init__(self):
        """Inicializar el cliente de Firestore."""
        try:
            # En Cloud Run, las credenciales se manejan automáticamente
            # Si hay un proyecto específico, se puede pasar como parámetro
            if settings.google_cloud_project:
                self.db = firestore.Client(project=settings.google_cloud_project)
            else:
                self.db = firestore.Client()
            
            self.collection_name = 'questions'
            logger.info("Cliente de Firestore inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando cliente de Firestore: {e}")
            raise FirestoreException(f"Error inicializando Firestore: {e}")
    
    async def get_question_by_id(self, question_id: str) -> Dict[str, Any]:
        """
        Obtiene una pregunta específica por su ID.
        
        Args:
            question_id: ID del documento de la pregunta
            
        Returns:
            dict: Datos de la pregunta
            
        Raises:
            HTTPException: Si no se encuentra la pregunta o hay un error
        """
        try:
            logger.info(f"Obteniendo pregunta con ID: {question_id}")
            
            doc_ref = self.db.collection(self.collection_name).document(question_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Pregunta no encontrada: {question_id}")
                raise create_http_exception(404, "Pregunta no encontrada")
            
            question_data = doc.to_dict()
            logger.info(f"Pregunta obtenida exitosamente: {question_id}")
            
            return question_data
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud obteniendo pregunta {question_id}: {e}")
            raise create_http_exception(500, f"Error de base de datos: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado obteniendo pregunta {question_id}: {e}")
            raise create_http_exception(500, f"Error interno: {e}")
    
    async def get_random_questions(
        self, 
        count: int = 5, 
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene preguntas aleatorias de la base de datos.
        
        Args:
            count: Número de preguntas a obtener
            subject: Filtro opcional por materia
            
        Returns:
            list: Lista de preguntas aleatorias
            
        Raises:
            HTTPException: Si hay un error en la consulta
        """
        try:
            logger.info(f"Obteniendo {count} preguntas aleatorias" + 
                       (f" de la materia: {subject}" if subject else ""))
            
            # Crear consulta base
            questions_query = self.db.collection(self.collection_name)
            
            # Agregar filtro por materia si se especifica
            if subject:
                questions_query = questions_query.where("subject", "==", subject)
            
            # Ejecutar consulta
            all_questions = []
            for doc in questions_query.stream():
                if doc.exists:
                    question_data = doc.to_dict()
                    # Agregar el ID del documento a los datos
                    question_data['id'] = doc.id
                    all_questions.append(question_data)
            
            # Verificar si se encontraron preguntas
            if not all_questions:
                logger.warning(f"No se encontraron preguntas" + 
                             (f" para la materia: {subject}" if subject else ""))
                return []
            
            # Asegurar que no pedimos más preguntas de las disponibles
            actual_count = min(count, len(all_questions))
            
            # Seleccionar preguntas aleatorias
            selected_questions = random.sample(all_questions, actual_count)
            
            logger.info(f"Obtenidas {len(selected_questions)} preguntas aleatorias")
            return selected_questions
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud obteniendo preguntas aleatorias: {e}")
            raise create_http_exception(500, f"Error de base de datos: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado obteniendo preguntas aleatorias: {e}")
            raise create_http_exception(500, f"Error interno: {e}")
    
    async def get_available_subjects(self) -> List[str]:
        """
        Obtiene la lista de materias disponibles.
        
        Returns:
            list: Lista de materias únicas
        """
        try:
            logger.info("Obteniendo materias disponibles")
            
            subjects = set()
            docs = self.db.collection(self.collection_name).select(['subject']).stream()
            
            for doc in docs:
                if doc.exists:
                    data = doc.to_dict()
                    if 'subject' in data and data['subject']:
                        subjects.add(data['subject'])
            
            subjects_list = sorted(list(subjects))
            logger.info(f"Encontradas {len(subjects_list)} materias: {subjects_list}")
            
            return subjects_list
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud obteniendo materias: {e}")
            raise create_http_exception(500, f"Error de base de datos: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado obteniendo materias: {e}")
            raise create_http_exception(500, f"Error interno: {e}")
    
    async def get_questions_count(self, subject: Optional[str] = None) -> int:
        """
        Obtiene el número total de preguntas disponibles.
        
        Args:
            subject: Filtro opcional por materia
            
        Returns:
            int: Número total de preguntas
        """
        try:
            logger.info("Obteniendo conteo de preguntas" + 
                       (f" para la materia: {subject}" if subject else ""))
            
            query = self.db.collection(self.collection_name)
            
            if subject:
                query = query.where("subject", "==", subject)
            
            # Usar aggregation query si está disponible, sino contar manualmente
            try:
                # Método más eficiente con aggregation query
                agg_query = query.count()
                results = agg_query.get()
                count = results[0][0].value
            except AttributeError:
                # Fallback: contar documentos manualmente
                docs = list(query.select([]).stream())
                count = len(docs)
            
            logger.info(f"Total de preguntas: {count}")
            return count
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud obteniendo conteo: {e}")
            raise create_http_exception(500, f"Error de base de datos: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado obteniendo conteo: {e}")
            raise create_http_exception(500, f"Error interno: {e}")