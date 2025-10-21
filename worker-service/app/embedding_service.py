import logging
from typing import List, Dict, Any
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for embedding text and storing in Qdrant"""
    
    def __init__(self):
        self.client = None
        self.encoder = None
        self._connect_qdrant()
        self._load_encoder()
    
    def _connect_qdrant(self):
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
            vector_size: Size of embedding vectors
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
                logger.info(f"Created collection: {collection_name} with vector size {vector_size}")
            else:
                logger.debug(f"Collection already exists: {collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def encode_text(self, text: str, task: str = "retrieval.passage", normalize: bool = True) -> List[float]:
        """
        Encode text to embedding vector
        
        Args:
            text: Text to encode
            task: Task type for Jina v3 (retrieval.passage for documents)
            normalize: L2 normalize the embedding (recommended)
            
        Returns:
            List[float]: Embedding vector
        """
        try:
            # Encode with task-specific prompt for Jina v3
            embedding = self.encoder.encode(
                text,
                task=task,
                convert_to_tensor=False,
                normalize_embeddings=normalize
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text with task '{task}': {e}")
            raise
    
    def process_and_store(
        self,
        product_code: str,
        tenant_id: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Process data, create embedding, and store in Qdrant
        
        Args:
            product_code: Product code for collection
            tenant_id: Tenant identifier
            data: Accounting object data
            metadata: Additional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure collection exists
            self.ensure_collection_exists(product_code, tenant_id)
            collection_name = self.get_collection_name(product_code, tenant_id)
            
            # Extract text to embed (accounting_object_name)
            text_to_embed = data.get("accounting_object_name", "")
            
            if not text_to_embed:
                logger.warning("No text to embed found in data")
                return False
            
            # Create embedding
            embedding_vector = self.encode_text(text_to_embed)
            
            # Prepare payload (metadata)
            payload = {
                "tenant_id": tenant_id,
                "product_code": product_code,
                "accounting_object_id": data.get("accounting_object_id"),
                "accounting_object_code": data.get("accounting_object_code"),
                "accounting_object_name": data.get("accounting_object_name"),
                "address": data.get("address"),
                "is_employee": data.get("is_employee", False),
                "is_employee_outside": data.get("is_employee_outside", False),
                "inactive": data.get("inactive", False),
                "is_customer_vendor": data.get("is_customer_vendor", False),
                "ihos_edit_version": data.get("ihos_edit_version", 0),
                "receipt_amount": data.get("receipt_amount"),
                "return_amount": data.get("return_amount"),
            }
            
            # Add additional metadata if provided
            if metadata:
                payload.update(metadata)
            
            # Generate point ID (use accounting_object_id or generate new UUID)
            point_id = str(data.get("accounting_object_id", uuid4()))
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding_vector,
                payload=payload
            )
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(
                f"✅ Stored: {data.get('accounting_object_code')} → {collection_name}"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error processing and storing data: {e}")
            return False
    
    def process_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Process batch of messages
        
        Args:
            messages: List of messages to process
            
        Returns:
            Dict with success and failure counts
        """
        success_count = 0
        failure_count = 0
        
        for message in messages:
            try:
                product_code = message.get("product_code")
                tenant_id = message.get("tenant_id")
                data = message.get("data")
                metadata = message.get("metadata", {})
                
                if not all([product_code, tenant_id, data]):
                    logger.warning(f"Invalid message format: {message}")
                    failure_count += 1
                    continue
                
                success = self.process_and_store(
                    product_code=product_code,
                    tenant_id=tenant_id,
                    data=data,
                    metadata=metadata
                )
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                failure_count += 1
        
        return {
            "success": success_count,
            "failure": failure_count,
            "total": len(messages)
        }

