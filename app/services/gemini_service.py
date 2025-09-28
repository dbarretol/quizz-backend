"""
Servicio para interactuar con la API de Gemini.
"""
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types, errors

from app.config.settings import settings
from app.core.exceptions import GeminiException, create_http_exception
from app.models.schemas import Question, UserAttempt

logger = logging.getLogger(__name__)


class GeminiService:
    """Servicio para generar contenido con Gemini AI."""
    
    def __init__(self):
        """Inicializar el cliente de Gemini."""
        try:
            self.client = genai.Client(
                api_key=settings.gemini_api_key,
                http_options=types.HttpOptions(api_version='v1alpha')
            )
            self.model = settings.gemini_model
            logger.info("Cliente de Gemini inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando cliente de Gemini: {e}")
            raise GeminiException(f"Error inicializando cliente de Gemini: {e}")
    
    async def generate_explanation(self, question_text: str) -> str:
        """
        Genera una explicación para una pregunta usando Gemini.
        
        Args:
            question_text: Texto de la pregunta a explicar
            
        Returns:
            str: Explicación generada
            
        Raises:
            GeminiException: Si ocurre un error al generar la explicación
        """
        try:
            logger.info(f"Generando explicación para: {question_text[:50]}...")
            
            if not question_text.strip():
                raise GeminiException("El texto de la pregunta no puede estar vacío")
            
            prompt = self._create_explanation_prompt(question_text)
            
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=types.Content(
                    role='user',
                    parts=[types.Part.from_text(text=prompt)]
                ),
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=settings.max_explanation_tokens,
                )
            )
            
            explanation_text = self._extract_text_from_response(response)
            logger.info(f"Explicación generada exitosamente, longitud: {len(explanation_text)}")
            
            return explanation_text
            
        except errors.ClientError as e:
            logger.error(f"Error del cliente Gemini: {e}")
            raise create_http_exception(400, f"Error del cliente: {e}")
            
        except errors.ServerError as e:
            logger.error(f"Error del servidor Gemini: {e}")
            raise create_http_exception(502, f"Error del servidor Gemini: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado generando explicación: {e}", exc_info=True)
            raise create_http_exception(500, f"Error interno: {e}")
    
    async def generate_feedback(self, questions: List[Question], user_attempt: UserAttempt) -> str:
        """
        Genera feedback personalizado basado en las respuestas del usuario.
        
        Args:
            questions: Lista de preguntas del quiz
            user_attempt: Intento del usuario con sus respuestas
            
        Returns:
            str: Feedback personalizado
            
        Raises:
            GeminiException: Si ocurre un error al generar el feedback
        """
        try:
            logger.info(f"Generando feedback para {len(questions)} preguntas")
            
            # Validar entrada
            self._validate_feedback_input(questions, user_attempt)
            
            # Identificar preguntas incorrectas
            incorrect_questions = self._get_incorrect_questions(questions, user_attempt)
            
            # Crear prompt basado en si hay preguntas incorrectas
            if not incorrect_questions:
                prompt = self._create_congratulations_prompt()
            else:
                prompt = self._create_feedback_prompt(incorrect_questions)
            
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=types.Content(
                    role='user',
                    parts=[types.Part.from_text(text=prompt)]
                ),
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    max_output_tokens=settings.max_feedback_tokens,
                )
            )
            
            feedback_text = self._extract_text_from_response(response)
            logger.info(f"Feedback generado exitosamente, longitud: {len(feedback_text)}")
            
            return feedback_text
            
        except errors.ClientError as e:
            logger.error(f"Error del cliente Gemini en feedback: {e}")
            raise create_http_exception(400, f"Error del cliente: {e}")
            
        except errors.ServerError as e:
            logger.error(f"Error del servidor Gemini en feedback: {e}")
            raise create_http_exception(502, f"Error del servidor Gemini: {e}")
            
        except Exception as e:
            logger.error(f"Error inesperado generando feedback: {e}", exc_info=True)
            raise create_http_exception(500, f"Error interno: {e}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conectividad con Gemini.
        
        Returns:
            dict: Resultado de la prueba
        """
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=types.Content(
                    role='user',
                    parts=[types.Part.from_text(text="Di 'Hola mundo'")]
                ),
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=10,
                )
            )
            
            if response and response.candidates:
                message = response.candidates[0].content.parts[0].text
                return {"status": "success", "message": message}
            else:
                return {"status": "error", "message": "No se recibió respuesta válida"}
                
        except Exception as e:
            logger.error(f"Error en test de Gemini: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_explanation_prompt(self, question_text: str) -> str:
        """Crea el prompt para generar explicaciones."""
        return f"""Explica de forma clara y concisa (máximo 100 palabras) la respuesta a la siguiente pregunta de cultura general, como si fueras un profesor. Usa formato Markdown:

Pregunta: {question_text}"""
    
    def _create_congratulations_prompt(self) -> str:
        """Crea el prompt para mensajes de felicitación."""
        return """Genera una breve felicitación en formato Markdown para un estudiante que respondió correctamente todas las preguntas de un quiz de cultura general. Máximo 100 palabras. Incluye una motivación para seguir aprendiendo."""
    
    def _create_feedback_prompt(self, incorrect_questions: List[Dict[str, Any]]) -> str:
        """Crea el prompt para feedback educativo."""
        prompt = f"""Eres un experto educador creando una **separata informativa** en formato Markdown para ayudar a un estudiante a repasar conceptos de cultura general.

**IMPORTANTE**: Esta separata será leída antes de que el estudiante vuelva a intentar el quiz, por lo que NO debes incluir de manera explícita o llamativa las respuestas, pero estas sí deben estar sutilmente incluidas en la separata generada.

**Preguntas que el estudiante respondió incorrectamente:**
"""
        
        for i, incorrect_q in enumerate(incorrect_questions, 1):
            prompt += f"{i}. {incorrect_q['question']}\n"
        
        prompt += """

**Instrucciones para la separata:**
1. Crea un documento educativo tipo boletín informativo
2. Aborda los TEMAS y CONCEPTOS relacionados con las preguntas incorrectas
3. NO reveles las respuestas correctas de manera explícita o llamativa, pero estas sí deben estar sutilmente incluidas en el texto generado.
4. Proporciona contexto histórico, geográfico o cultural relevante
5. Incluye datos curiosos o información complementaria
6. Usa formato Markdown con títulos, subtítulos y listas
7. Máximo 500 palabras
8. Estilo: informativo, educativo y atractivo
9. El objetivo es que el usuario aprenda los conceptos para responder mejor en un segundo intento

Genera la separata educativa ahora:"""
        
        return prompt
    
    def _extract_text_from_response(self, response) -> str:
        """Extrae texto de la respuesta de Gemini."""
        if not response:
            raise GeminiException("No se recibió respuesta de Gemini")
        
        if not hasattr(response, 'candidates') or not response.candidates:
            raise GeminiException("No se encontraron candidatos en la respuesta")
        
        candidate = response.candidates[0]
        
        if not hasattr(candidate, 'content') or not candidate.content:
            raise GeminiException("El candidato no tiene contenido")
        
        if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
            raise GeminiException("El contenido no tiene partes")
        
        text = candidate.content.parts[0].text
        
        if not text or not text.strip():
            raise GeminiException("El texto generado está vacío")
        
        return text
    
    def _validate_feedback_input(self, questions: List[Question], user_attempt: UserAttempt):
        """Valida la entrada para generación de feedback."""
        if not questions:
            raise GeminiException("La lista de preguntas no puede estar vacía")
        
        if len(questions) != user_attempt.total_questions:
            raise GeminiException("El número de preguntas no coincide con total_questions")
        
        if len(user_attempt.answers) != len(questions):
            raise GeminiException("El número de respuestas no coincide con el número de preguntas")
    
    def _get_incorrect_questions(self, questions: List[Question], user_attempt: UserAttempt) -> List[Dict[str, Any]]:
        """Identifica las preguntas respondidas incorrectamente."""
        incorrect_questions = []
        
        for i, question in enumerate(questions):
            user_answer_idx = user_attempt.answers[i]
            correct_answer_idx = question.correct_answer
            
            if user_answer_idx != correct_answer_idx:
                incorrect_questions.append({
                    'question': question.question,
                    'options': question.options
                })
        
        return incorrect_questions