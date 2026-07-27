FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias primero (capa cacheada)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

# Ingesta en startup (necesita GOOGLE_API_KEY en runtime, no en build)
CMD ["sh", "-c", "python scripts/ingest.py && python app/main.py"]
