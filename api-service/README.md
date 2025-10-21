# Semantic Search API Service

FastAPI service providing semantic search capabilities using Qdrant vector database and Kafka message queue.

## Features

- **Semantic Search**: Search accounting objects by meaning using multilingual embeddings
- **Kafka Integration**: Push data to Kafka queue for asynchronous embedding processing
- **Multi-tenant Support**: Filter by product_code and tenant_id
- **Batch Processing**: Support for batch data ingestion

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Qdrant connection details
- Kafka bootstrap servers
- Embedding model preferences

## Running the Service

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Search
```bash
POST /api/v1/search
```

Search for accounting objects by semantic similarity.

**Request:**
```json
{
  "query": "công ty cấp nước",
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-123",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "score": 0.95,
      "metadata": {...},
      "accounting_object_id": "uuid",
      "accounting_object_code": "CTCPCNST",
      "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
      "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội"
    }
  ],
  "total": 1,
  "query": "công ty cấp nước",
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-123"
}
```

### Push Data
```bash
POST /api/v1/push
```

Push single accounting object to Kafka for embedding.

**Request:**
```json
{
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-123",
  "data": {
    "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
    "accounting_object_code": "CTCPCNST",
    "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
    "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
    "is_employee": false,
    "is_employee_outside": false,
    "inactive": false,
    "is_customer_vendor": false,
    "ihos_edit_version": 0
  }
}
```

### Push Batch Data
```bash
POST /api/v1/push/batch
```

Push multiple accounting objects to Kafka.

**Request:**
```json
{
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-123",
  "data_list": [
    {...},
    {...}
  ]
}
```

## Architecture

- **FastAPI**: Modern Python web framework
- **Qdrant**: Vector database for semantic search
- **Kafka**: Message queue for asynchronous processing
- **Sentence Transformers**: Multilingual embedding model

## Dependencies

- Python 3.8+
- Qdrant server
- Kafka broker

