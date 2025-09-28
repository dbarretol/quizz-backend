# Quiz Service API

API service para manejo de quizzes con explicaciones y feedback personalizado generado por IA.

## 🚀 Características

- **Gestión de preguntas**: Obtener preguntas aleatorias y específicas desde Firestore
- **Explicaciones IA**: Generar explicaciones detalladas usando Gemini AI
- **Feedback personalizado**: Crear separatas educativas basadas en respuestas incorrectas
- **Arquitectura limpia**: Código organizado, modular y bien documentado
- **Validación robusta**: Validación de datos con Pydantic
- **Manejo de errores**: Sistema robusto de manejo de excepciones

## 🛠️ Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **Google Cloud Firestore**: Base de datos NoSQL
- **Google Gemini AI**: Modelo de IA para generación de contenido
- **Pydantic**: Validación y serialización de datos
- **Uvicorn**: Servidor ASGI

## 📁 Estructura del proyecto

```
quiz-service/
├── app/
│   ├── main.py                 # Punto de entrada principal
│   ├── config/
│   │   └── settings.py         # Configuración centralizada
│   ├── core/
│   │   ├── exceptions.py       # Excepciones personalizadas
│   │   └── logging.py          # Configuración de logging
│   ├── models/
│   │   └── schemas.py          # Modelos Pydantic
│   ├── services/
│   │   ├── firestore_service.py # Lógica de Firestore
│   │   └── gemini_service.py    # Lógica de Gemini
│   ├── api/
│   │   ├── deps.py             # Dependencias
│   │   └── v1/
│   │       ├── router.py       # Router principal
│   │       └── endpoints/      # Endpoints organizados
│   └── templates/
│       └── template.html
├── gcp-key.json               # Credenciales de Google Cloud
├── .env                       # Variables de entorno
├── requirements.txt
└── README.md
```

## ⚙️ Configuración

### 1. Variables de entorno

Crear archivo `.env`:

```bash
# Gemini AI
GEMINI_API_KEY=tu_api_key_de_gemini

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json

# Entorno
ENVIRONMENT=development
```

### 2. Credenciales de Google Cloud

Colocar el archivo `gcp-key.json` con las credenciales de service account en la raíz del proyecto.

### 3. Instalación de dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Ejecución

### Desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## 📚 Endpoints de la API

### Questions

- `GET /api/v1/questions/` - Obtener preguntas aleatorias
- `GET /api/v1/questions/{id}` - Obtener pregunta específica
- `GET /api/v1/questions/subjects/available` - Listar materias disponibles
- `GET /api/v1/questions/count/total` - Contar preguntas totales

### Explanations

- `POST /api/v1/explanations/generate` - Generar explicación
- `GET /api/v1/explanations/test` - Probar conexión con Gemini

### Feedback

- `POST /api/v1/feedback/generate` - Generar feedback personalizado

## 📖 Ejemplos de uso

### Obtener preguntas aleatorias

```bash
curl -X GET "http://localhost:8000/api/v1/questions/?count=5&subject=Historia"
```

### Generar explicación

```bash
curl -X POST "http://localhost:8000/api/v1/explanations/generate" \
  -H "Content-Type: application/json" \
  -d '{"question_text": "¿Cuál es la capital de Francia?"}'
```

### Generar feedback

```bash
curl -X POST "http://localhost:8000/api/v1/feedback/generate" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 🐳 Docker (Opcional)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY gcp-key.json .
COPY .env .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Build y run

```bash
docker build -t quiz-service .
docker run -p 8080:8080 quiz-service
```

## 🔧 Configuración para Google Cloud Run

### cloudbuild.yaml

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/quiz-service', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/quiz-service']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'quiz-service'
      - '--image=gcr.io/$PROJECT_ID/quiz-service'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest
```

## 📝 Logging

Los logs se configuran automáticamente y incluyen:

- Timestamp
- Level (INFO, ERROR, etc.)
- Nombre del logger
- Mensaje

## 🚨 Manejo de errores

El sistema incluye:

- Excepciones personalizadas por servicio
- Manejo robusto de errores de Google Cloud
- Respuestas HTTP estructuradas
- Logging detallado de errores

## 🔒 Seguridad

- Validación de entrada con Pydantic
- Configuración CORS personalizable
- Variables de entorno para credenciales
- Límites en parámetros de entrada

## 📈 Monitoreo

Para producción, considerar agregar:

- Prometheus metrics
- Health checks detallados
- Distributed tracing
- APM (Application Performance Monitoring)

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT.