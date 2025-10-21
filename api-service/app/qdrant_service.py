import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.text_processor import TextProcessor, SearchEnhancer

logger = logging.getLogger(__name__)

# Import cache service (will be set by main.py)
_cache_service = None

def set_cache_service(cache):
    """Set global cache service"""
    global _cache_service
    _cache_service = cache


class QdrantService:
    """Service for interacting with Qdrant vector database"""
    
    def __init__(self):
        self.client = None
        self.encoder = None
        self._connect()
        self._load_encoder()
    
    def _connect(self):
        """Connect to Qdrant database"""
        try:
            if settings.QDRANT_API_KEY:
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                    https=False,  # Use HTTP instead of HTTPS
                    prefer_grpc=False  # Use REST API instead of gRPC
                )
            else:
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    https=False,
                    prefer_grpc=False
                )
            logger.info(f"Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def _load_encoder(self):
        """Load sentence transformer model"""
        try:
            # For Jina v3, need trust_remote_code=True
            self.encoder = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                trust_remote_code=True
            )
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def get_collection_name(self, product_code: str, tenant_id: str) -> str:
        """
        Generate collection name based on product code and tenant ID
        
        Args:
            product_code: Product code identifier
            tenant_id: Tenant identifier
            
        Returns:
            str: Collection name in format [product_code]_[tenant_id]
        """
        # Clean product_code and tenant_id
        clean_product = product_code.lower().replace(' ', '_').replace('-', '_')
        clean_tenant = tenant_id.lower().replace(' ', '_').replace('-', '_')
        return f"{clean_product}_{clean_tenant}"
    
    def ensure_collection_exists(self, product_code: str, tenant_id: str, vector_size: int = 1024):
        """
        Ensure collection exists, create if not
        
        Args:
            product_code: Product code for collection
            tenant_id: Tenant identifier
            vector_size: Size of embedding vectors (default 1024 for Jina v3)
        """
        collection_name = self.get_collection_name(product_code, tenant_id)
        
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {collection_name}")
            else:
                logger.debug(f"Collection already exists: {collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def encode_text(self, text: str, task: str = "retrieval.query", normalize: bool = True) -> List[float]:
        """
        Encode text to embedding vector with caching
        
        Args:
            text: Text to encode
            task: Task type for Jina v3 (retrieval.query or retrieval.passage)
            normalize: L2 normalize the embedding (recommended)
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            # Create cache key with task
            cache_key = f"{task}:{text}"
            
            # Try cache first
            if _cache_service:
                cached = _cache_service.get_embedding(cache_key)
                if cached is not None:
                    return cached
            
            # Encode with task-specific prompt for Jina v3
            embedding = self.encoder.encode(
                text,
                task=task,
                convert_to_tensor=False,
                normalize_embeddings=normalize
            )
            
            embedding_list = embedding.tolist()
            
            # Cache the result
            if _cache_service:
                _cache_service.set_embedding(cache_key, embedding_list)
            
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error encoding text with task '{task}': {e}")
            raise
    
    def search(
        self,
        query: str,
        product_code: str,
        tenant_id: str,
        limit: int = 10,
        use_query_expansion: bool = False,
        use_reranking: bool = True,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search with caching
        
        Args:
            query: Search query text
            product_code: Product code for collection
            tenant_id: Tenant identifier
            limit: Maximum number of results
            use_query_expansion: Whether to expand query (default: False for speed)
            use_reranking: Whether to boost score with text match (default: True)
            min_score: Minimum score threshold (0-1)
            
        Returns:
            List of search results with scores and metadata
        """
        # Try cache first
        if _cache_service:
            cached_results = _cache_service.get_search_results(
                query=query,
                product_code=product_code,
                tenant_id=tenant_id,
                limit=limit,
                use_query_expansion=use_query_expansion,
                use_reranking=use_reranking,
                min_score=min_score
            )
            if cached_results is not None:
                return cached_results
        
        collection_name = self.get_collection_name(product_code, tenant_id)
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if collection_name not in collection_names:
                logger.warning(f"Collection {collection_name} does not exist")
                return []
            
            # Normalize query
            normalized_query = TextProcessor.normalize_text(query)
            
            # Encode query with task="retrieval.query" for Jina v3
            query_vector = self.encode_text(normalized_query, task="retrieval.query", normalize=True)
            
            # Create filter for tenant_id
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="tenant_id",
                        match=MatchValue(value=tenant_id)
                    )
                ]
            )
            
            # Perform search
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=search_filter,
                limit=limit * 2  # Get more for re-ranking
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "score": result.score,
                    "metadata": result.payload
                })
            
            # Boost score with simple text matching
            if use_reranking and results:
                for result in results:
                    metadata = result.get("metadata", {})
                    name = metadata.get("accounting_object_name", "")
                    code = metadata.get("accounting_object_code", "")
                    
                    # Simple keyword boost
                    original_score = result["score"]
                    boost = 0.0
                    
                    # Normalize for comparison
                    name_lower = TextProcessor.normalize_text(name)
                    query_lower = normalized_query
                    
                    # Exact match boost
                    if query_lower in name_lower:
                        boost = 0.3
                    # Partial word match boost
                    elif any(word in name_lower for word in query_lower.split()):
                        boost = 0.15
                    
                    # Code match boost
                    if code and query_lower in code.lower():
                        boost += 0.1
                    
                    # Apply boost (max 1.0)
                    result["original_score"] = original_score
                    result["score"] = min(original_score + boost, 1.0)
                
                # Sort by boosted score
                results.sort(key=lambda x: x["score"], reverse=True)
            
            # Filter by minimum score
            if min_score > 0:
                results = [r for r in results if r["score"] >= min_score]
            
            # Limit final results
            results = results[:limit]
            
            # Cache the results
            if _cache_service:
                _cache_service.set_search_results(
                    query=query,
                    product_code=product_code,
                    tenant_id=tenant_id,
                    limit=limit,
                    results=results,
                    use_query_expansion=use_query_expansion,
                    use_reranking=use_reranking,
                    min_score=min_score
                )
            
            logger.info(f"Found {len(results)} results for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise


# Global Qdrant service instance
qdrant_service = QdrantService()

