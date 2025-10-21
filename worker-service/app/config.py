from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Worker Settings
    WORKER_NAME: str = "embedding-worker"
    LOG_LEVEL: str = "INFO"
    
    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "embedding-requests"
    KAFKA_GROUP_ID: str = "embedding-worker-group"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    
    # Embedding Settings
    # Using Jina Embeddings v3 - excellent multilingual model
    EMBEDDING_MODEL: str = "jinaai/jina-embeddings-v3"
    EMBEDDING_TASK: str = "retrieval.passage"  # Task type for documents
    VECTOR_SIZE: int = 1024  # Jina v3 dimensions
    
    # Processing Settings
    BATCH_SIZE: int = 100
    BATCH_TIMEOUT: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

