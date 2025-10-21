import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.models import (
    EmbeddingRequest,
    EmbeddingBatchRequest,
    SearchRequest,
    SearchResponse,
    SearchResult,
    MessageResponse
)
from app.kafka_producer import kafka_producer
from app.qdrant_service import qdrant_service, set_cache_service
from app.text_processor import TextProcessor
from app.cache_service import CacheService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting up API service...")
    
    # Initialize Redis cache
    if settings.REDIS_ENABLED:
        try:
            cache = CacheService(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                enabled=settings.REDIS_ENABLED,
                ttl=settings.REDIS_TTL
            )
            set_cache_service(cache)
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
    
    # Load custom synonyms and abbreviations if configured
    if settings.CUSTOM_SYNONYMS_FILE:
        synonyms_path = Path(settings.CUSTOM_SYNONYMS_FILE)
        if synonyms_path.exists():
            TextProcessor.load_custom_synonyms(str(synonyms_path))
        else:
            logger.warning(f"Custom synonyms file not found: {settings.CUSTOM_SYNONYMS_FILE}")
    
    if settings.CUSTOM_ABBREVIATIONS_FILE:
        abbr_path = Path(settings.CUSTOM_ABBREVIATIONS_FILE)
        if abbr_path.exists():
            TextProcessor.load_custom_abbreviations(str(abbr_path))
        else:
            logger.warning(f"Custom abbreviations file not found: {settings.CUSTOM_ABBREVIATIONS_FILE}")
    
    yield
    logger.info("Shutting down API service...")
    kafka_producer.close()


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return MessageResponse(
        message="Semantic Search API is running",
        details={
            "version": settings.API_VERSION,
            "endpoints": {
                "search": "/api/v1/search",
                "push": "/api/v1/push",
                "push_batch": "/api/v1/push/batch"
            }
        }
    )


@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint"""
    return MessageResponse(message="Service is healthy")


@app.get("/cache/stats", response_model=MessageResponse)
async def cache_stats():
    """Get cache statistics"""
    from app import qdrant_service
    
    cache = qdrant_service._cache_service
    if cache and cache.enabled:
        stats = cache.get_stats()
        return MessageResponse(
            message="Cache statistics",
            details=stats
        )
    else:
        return MessageResponse(
            message="Cache is disabled",
            details={"enabled": False}
        )


@app.post("/api/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Semantic search endpoint
    
    Search for accounting objects by semantic similarity
    Returns top N results filtered by product_code and tenant_id
    """
    try:
        logger.info(
            f"Search request - Query: {request.query}, "
            f"Product: {request.product_code}, Tenant: {request.tenant_id}"
        )
        
        # Perform search with enhancements
        results = qdrant_service.search(
            query=request.query,
            product_code=request.product_code,
            tenant_id=request.tenant_id,
            limit=request.limit,
            use_query_expansion=request.use_query_expansion,
            use_reranking=request.use_reranking,
            min_score=request.min_score
        )
        
        # Format response
        search_results = []
        for result in results:
            metadata = result["metadata"]
            search_results.append(
                SearchResult(
                    score=result["score"],
                    metadata=metadata,
                    accounting_object_id=metadata.get("accounting_object_id"),
                    accounting_object_code=metadata.get("accounting_object_code"),
                    accounting_object_name=metadata.get("accounting_object_name"),
                    address=metadata.get("address")
                )
            )
        
        return SearchResponse(
            results=search_results,
            total=len(search_results),
            query=request.query,
            product_code=request.product_code,
            tenant_id=request.tenant_id
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/api/v1/push", response_model=MessageResponse)
async def push_data(request: EmbeddingRequest):
    """
    Push data to Kafka for embedding processing
    
    Sends accounting object data to Kafka queue for worker to process
    and store in Qdrant vector database
    """
    try:
        logger.info(
            f"Push request - Product: {request.product_code}, "
            f"Tenant: {request.tenant_id}, "
            f"Object: {request.data.accounting_object_code}"
        )
        
        # Prepare message
        message = {
            "product_code": request.product_code,
            "tenant_id": request.tenant_id,
            "data": request.data.model_dump(),
            "metadata": request.metadata or {}
        }
        
        # Send to Kafka
        success = kafka_producer.send_embedding_request(message)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message to Kafka"
            )
        
        return MessageResponse(
            message="Data pushed to processing queue successfully",
            details={
                "product_code": request.product_code,
                "tenant_id": request.tenant_id,
                "accounting_object_id": str(request.data.accounting_object_id)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Push error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Push failed: {str(e)}"
        )


@app.post("/api/v1/push/batch", response_model=MessageResponse)
async def push_batch_data(request: EmbeddingBatchRequest):
    """
    Push batch data to Kafka for embedding processing
    
    Sends multiple accounting objects to Kafka queue for processing
    """
    try:
        logger.info(
            f"Batch push request - Product: {request.product_code}, "
            f"Tenant: {request.tenant_id}, "
            f"Count: {len(request.data_list)}"
        )
        
        success_count = 0
        failed_count = 0
        
        for data in request.data_list:
            message = {
                "product_code": request.product_code,
                "tenant_id": request.tenant_id,
                "data": data.model_dump(),
                "metadata": {}
            }
            
            success = kafka_producer.send_embedding_request(message)
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return MessageResponse(
            message=f"Batch push completed",
            details={
                "product_code": request.product_code,
                "tenant_id": request.tenant_id,
                "total": len(request.data_list),
                "success": success_count,
                "failed": failed_count
            }
        )
        
    except Exception as e:
        logger.error(f"Batch push error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch push failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

