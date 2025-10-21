# System Architecture

## Tổng quan kiến trúc

Hệ thống Semantic Search được thiết kế theo kiến trúc microservices với message queue để xử lý bất đồng bộ.

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│                    (Web/Mobile/API)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     API SERVICE                             │
│                      (FastAPI)                              │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Search     │  │    Push      │  │   Health     │    │
│  │   Endpoint   │  │   Endpoint   │  │   Check      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└──────────┬─────────────────┬────────────────────────────────┘
           │                 │
           │                 │ Produce Message
           │                 ▼
           │        ┌─────────────────┐
           │        │     KAFKA       │
           │        │  Message Queue  │
           │        └────────┬────────┘
           │                 │
           │                 │ Consume Message
           │                 ▼
           │        ┌─────────────────────────────┐
           │        │    WORKER SERVICE           │
           │        │   (Kafka Consumer)          │
           │        │                             │
           │        │  ┌──────────────────────┐  │
           │        │  │  Embedding Service   │  │
           │        │  │  - Load Model        │  │
           │        │  │  - Create Vectors    │  │
           │        │  │  - Store in Qdrant   │  │
           │        │  └──────────────────────┘  │
           │        └─────────────┬───────────────┘
           │                      │
           │ Query Vector         │ Upsert Vector + Metadata
           │                      │
           ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    QDRANT DATABASE                          │
│                  (Vector Database)                          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Collections (per product_code)                    │   │
│  │                                                     │   │
│  │  product_accounting/                               │   │
│  │  ├── Vector (384 dim)                              │   │
│  │  └── Payload:                                      │   │
│  │      ├── tenant_id                                 │   │
│  │      ├── accounting_object_id                      │   │
│  │      ├── accounting_object_code                    │   │
│  │      ├── accounting_object_name                    │   │
│  │      ├── address                                   │   │
│  │      └── ... (other metadata)                      │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. API Service (FastAPI)

**Trách nhiệm:**
- Nhận request từ client
- Xử lý tìm kiếm ngữ nghĩa
- Đẩy dữ liệu lên Kafka queue
- Validate input data

**Endpoints:**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/search` - Semantic search
- `POST /api/v1/push` - Push single record
- `POST /api/v1/push/batch` - Push batch records

**Technologies:**
- FastAPI - Web framework
- Pydantic - Data validation
- kafka-python - Kafka producer
- qdrant-client - Vector database client
- sentence-transformers - Embedding model

### 2. Worker Service (Kafka Consumer)

**Trách nhiệm:**
- Lắng nghe Kafka topic
- Xử lý embedding cho text
- Lưu trữ vectors vào Qdrant
- Batch processing để tối ưu

**Flow:**
1. Consume message từ Kafka
2. Extract `accounting_object_name`
3. Generate embedding vector (384 dimensions)
4. Prepare metadata payload
5. Upsert to Qdrant collection

**Technologies:**
- kafka-python - Kafka consumer
- sentence-transformers - Embedding model
- qdrant-client - Vector database client

### 3. Kafka (Message Queue)

**Trách nhiệm:**
- Message broker giữa API và Worker
- Đảm bảo message delivery
- Support scaling workers

**Configuration:**
- Topic: `embedding-requests`
- Replication factor: 1 (có thể tăng cho production)
- Auto create topics: enabled

### 4. Qdrant (Vector Database)

**Trách nhiệm:**
- Lưu trữ embedding vectors
- Hỗ trợ similarity search
- Lưu trữ metadata

**Configuration:**
- Distance metric: Cosine similarity
- Vector size: 384 (MiniLM model)
- Collections: Dynamic per product_code

### 5. Zookeeper

**Trách nhiệm:**
- Quản lý Kafka cluster
- Coordination service

## Data Flow

### Push Data Flow

```
1. Client → API Service
   POST /api/v1/push
   {
     "product_code": "ACCOUNTING",
     "tenant_id": "tenant-123",
     "data": {...}
   }

2. API Service → Kafka
   Produce message to topic "embedding-requests"

3. Kafka → Worker Service
   Consumer receives message

4. Worker Service
   - Load embedding model
   - Extract accounting_object_name
   - Generate vector (384 dim)
   - Prepare payload with all metadata

5. Worker Service → Qdrant
   Upsert point to collection "product_accounting"
   - id: accounting_object_id
   - vector: [0.123, -0.456, ...]
   - payload: {tenant_id, ...metadata}

6. API Service → Client
   Response: {"message": "success", ...}
```

### Search Flow

```
1. Client → API Service
   POST /api/v1/search
   {
     "query": "công ty cấp nước",
     "product_code": "ACCOUNTING",
     "tenant_id": "tenant-123",
     "limit": 10
   }

2. API Service
   - Load embedding model
   - Generate query vector from text

3. API Service → Qdrant
   Search in collection "product_accounting"
   - Filter: tenant_id = "tenant-123"
   - Vector: query_vector
   - Limit: 10

4. Qdrant → API Service
   Return top 10 similar vectors with scores

5. API Service → Client
   Response: {
     "results": [
       {
         "score": 0.95,
         "accounting_object_name": "...",
         "metadata": {...}
       }
     ],
     "total": 10
   }
```

## Scalability

### Horizontal Scaling

**API Service:**
- Stateless design
- Có thể chạy nhiều instances
- Load balancer phân phối traffic

**Worker Service:**
- Kafka consumer group
- Có thể chạy nhiều workers
- Kafka tự động phân phối messages

**Qdrant:**
- Hỗ trợ clustering
- Sharding cho large datasets

**Kafka:**
- Tăng partitions cho topic
- Tăng replication factor

### Vertical Scaling

**API Service:**
- Tăng CPU cho faster embedding
- Tăng RAM cho model caching

**Worker Service:**
- Tăng CPU cho parallel processing
- Tăng RAM cho batch processing

**Qdrant:**
- Tăng RAM cho in-memory vectors
- SSD storage cho faster I/O

## Performance Optimization

### 1. Batch Processing
- Worker xử lý nhiều messages cùng lúc
- Giảm overhead của network calls

### 2. Model Caching
- Embedding model được load 1 lần
- Reuse cho tất cả requests

### 3. Connection Pooling
- Reuse Kafka connections
- Reuse Qdrant connections

### 4. Async Processing
- API không đợi embedding hoàn thành
- Client nhận response ngay lập tức

## Security Considerations

### 1. API Security
- Add authentication (JWT, API Key)
- Rate limiting
- Input validation

### 2. Network Security
- Internal network cho services
- Expose chỉ API service ra ngoài
- TLS/SSL cho production

### 3. Data Security
- Encrypt sensitive data
- Access control cho Qdrant
- Kafka authentication

## Monitoring & Logging

### Metrics to Monitor

**API Service:**
- Request rate
- Response time
- Error rate
- Active connections

**Worker Service:**
- Messages processed/sec
- Processing time per message
- Error rate
- Queue lag

**Qdrant:**
- Query latency
- Storage usage
- Collection sizes

**Kafka:**
- Message throughput
- Consumer lag
- Partition distribution

### Logging Strategy

**Structured Logging:**
- JSON format
- Timestamp
- Service name
- Request ID
- Log level

**Log Aggregation:**
- Centralized logging (ELK, Grafana Loki)
- Log retention policy
- Alert on errors

## Disaster Recovery

### Backup Strategy

**Qdrant:**
- Regular snapshots
- Backup to S3/GCS
- Point-in-time recovery

**Kafka:**
- Message retention policy
- Backup consumer offsets
- Replay capability

### High Availability

**Multiple Instances:**
- Run multiple API instances
- Run multiple workers
- Kafka replication
- Qdrant clustering

## Future Enhancements

1. **Advanced Search:**
   - Hybrid search (vector + keyword)
   - Filters on metadata fields
   - Faceted search

2. **Performance:**
   - GPU acceleration for embeddings
   - Quantization for smaller vectors
   - Caching layer (Redis)

3. **Features:**
   - Real-time updates
   - Incremental indexing
   - Multi-model support

4. **Operations:**
   - Kubernetes deployment
   - Auto-scaling
   - Circuit breakers
   - Health checks with retries

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| API Framework | FastAPI | 0.109.0 | REST API |
| Message Queue | Kafka | 7.5.0 | Async processing |
| Vector DB | Qdrant | 1.7.4 | Similarity search |
| Embedding | Sentence Transformers | 2.3.1 | Text to vector |
| Model | MiniLM-L12-v2 | - | Multilingual |
| Language | Python | 3.11 | All services |
| Container | Docker | - | Deployment |
| Orchestration | Docker Compose | - | Local dev |

## Conclusion

Kiến trúc này cung cấp:
- ✅ Scalability - Dễ dàng scale theo nhu cầu
- ✅ Reliability - Message queue đảm bảo không mất data
- ✅ Performance - Async processing, batch optimization
- ✅ Maintainability - Microservices, clear separation
- ✅ Flexibility - Dễ dàng thêm features mới

