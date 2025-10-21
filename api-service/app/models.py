from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from uuid import UUID


class AccountingObject(BaseModel):
    """Model for accounting object data"""
    accounting_object_id: UUID
    accounting_object_code: str
    accounting_object_name: str
    address: Optional[str] = None
    is_employee: bool = False
    is_employee_outside: bool = False
    inactive: bool = False
    is_customer_vendor: bool = False
    ihos_edit_version: int = 0
    receipt_amount: Optional[float] = None
    return_amount: Optional[float] = None


class EmbeddingRequest(BaseModel):
    """Request model for pushing data to Kafka"""
    product_code: str = Field(..., description="Product code for collection grouping")
    tenant_id: str = Field(..., description="Tenant identifier")
    data: AccountingObject = Field(..., description="Accounting object data to embed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class EmbeddingBatchRequest(BaseModel):
    """Request model for batch pushing data to Kafka"""
    product_code: str = Field(..., description="Product code for collection grouping")
    tenant_id: str = Field(..., description="Tenant identifier")
    data_list: list[AccountingObject] = Field(..., description="List of accounting objects to embed")


class SearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query text")
    product_code: str = Field(..., description="Product code for collection filtering")
    tenant_id: str = Field(..., description="Tenant identifier")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    use_query_expansion: bool = Field(default=False, description="Expand query with synonyms (slower)")
    use_reranking: bool = Field(default=True, description="Boost score with keyword matching")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum score threshold")


class SearchResult(BaseModel):
    """Single search result"""
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    accounting_object_id: UUID
    accounting_object_code: str
    accounting_object_name: str
    address: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search results"""
    results: list[SearchResult]
    total: int
    query: str
    product_code: str
    tenant_id: str


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    status: str = "success"
    details: Optional[Dict[str, Any]] = None

