from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Semantic Search API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "embedding-requests"
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "keepitreal/vietnamese-sbert"
    
    # Search Enhancement Settings
    CUSTOM_SYNONYMS_FILE: Optional[str] = None  # Path to custom synonyms JSON file
    CUSTOM_ABBREVIATIONS_FILE: Optional[str] = None  # Path to custom abbreviations JSON file
    
    # Redis Cache Settings
    REDIS_ENABLED: bool = True  # Enable Redis caching
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

