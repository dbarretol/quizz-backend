FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Copiar archivo .env si existe (opcional para variables no sensibles)
COPY .env* ./

# Exponer puerto
EXPOSE 8080

# Variables de entorno para Cloud Run
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]