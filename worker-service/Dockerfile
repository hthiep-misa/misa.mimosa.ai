FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model during build to speed up startup
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('keepitreal/vietnamese-sbert')"

# Copy application code
COPY app/ ./app/

# Run the worker
CMD ["python", "-m", "app.kafka_consumer"]

