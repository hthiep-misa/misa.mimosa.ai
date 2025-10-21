# Embedding Worker Service

Kafka consumer worker that processes embedding requests and stores vectors in Qdrant database.

## Features

- **Kafka Consumer**: Listens to Kafka topic for embedding requests
- **Batch Processing**: Processes messages in batches for efficiency
- **Automatic Embedding**: Generates embeddings using multilingual models
- **Qdrant Storage**: Stores embeddings with metadata in Qdrant collections
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals properly

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
- Kafka bootstrap servers and topic
- Embedding model preferences
- Batch processing settings

## Running the Worker

```bash
python -m app.kafka_consumer
```

## How It Works

1. **Listen**: Worker connects to Kafka and listens for messages on configured topic
2. **Receive**: Messages contain accounting object data with product_code and tenant_id
3. **Embed**: Worker extracts `accounting_object_name` and creates embedding vector
4. **Store**: Embedding and metadata are stored in Qdrant collection (grouped by product_code)
5. **Filter**: Data is tagged with tenant_id for multi-tenant filtering

## Message Format

Expected message format from Kafka:

```json
{
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-123",
  "data": {
    "accounting_object_id": "uuid",
    "accounting_object_code": "CTCPCNST",
    "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
    "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
    "is_employee": false,
    "is_employee_outside": false,
    "inactive": false,
    "is_customer_vendor": false,
    "ihos_edit_version": 0,
    "receipt_amount": null,
    "return_amount": null
  },
  "metadata": {}
}
```

## Collection Structure

- Collections are created per product_code: `product_{product_code}`
- Each document contains:
  - **Vector**: Embedding of `accounting_object_name`
  - **Payload**: All accounting object fields + tenant_id for filtering

## Logging

Worker logs all activities including:
- Connection status
- Messages processed
- Batch statistics
- Errors and warnings

## Graceful Shutdown

Press `Ctrl+C` or send SIGTERM to gracefully shutdown:
- Completes current batch processing
- Commits Kafka offsets
- Closes connections properly

## Dependencies

- Python 3.8+
- Kafka broker
- Qdrant server

