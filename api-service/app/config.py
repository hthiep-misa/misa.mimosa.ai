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
    # Using Jina Embeddings v3 - excellent multilingual model
    # Can be either HuggingFace model name or local path (e.g., "./models/jina-embeddings-v3")
    EMBEDDING_MODEL: str = "jinaai/jina-embeddings-v3"
    EMBEDDING_TASK: str = "retrieval.passage"  # Task type for documents (not used in API, but for consistency)
    EMBEDDING_DIMENSIONS: int = 1024  # Jina v3 dimensions
    
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

