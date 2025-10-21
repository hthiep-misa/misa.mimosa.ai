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
    EMBEDDING_MODEL: str = "keepitreal/vietnamese-sbert"
    VECTOR_SIZE: int = 768  # Size for Vietnamese-SBERT model (PhoBERT-based)
    
    # Processing Settings
    BATCH_SIZE: int = 100
    BATCH_TIMEOUT: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

