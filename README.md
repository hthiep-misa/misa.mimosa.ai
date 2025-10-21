# MISA MIMOSA ONLINE AI - Semantic Search System

Hệ thống tìm kiếm ngữ nghĩa (Semantic Search) cho dữ liệu kế toán sử dụng FastAPI, Kafka, và Qdrant.

## Tổng quan

Hệ thống bao gồm 2 services chính:

1. **API Service**: FastAPI REST API cung cấp endpoints cho tìm kiếm và đẩy dữ liệu
2. **Worker Service**: Kafka consumer xử lý embedding và lưu trữ vào Qdrant

## Kiến trúc

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Client    │─────▶│ API Service │─────▶│    Kafka    │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                      │
                            │                      ▼
                            │              ┌─────────────┐
                            │              │   Worker    │
                            │              │   Service   │
                            │              └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌─────────────────────────────┐
                     │   Qdrant Vector Database    │
                     └─────────────────────────────┘
```

## Tính năng

### API Service
- ✅ Tìm kiếm ngữ nghĩa theo `accounting_object_name`
- ✅ Lọc theo `product_code` và `tenant_id`
- ✅ Trả về top 10 kết quả với metadata đầy đủ
- ✅ Push dữ liệu đơn lẻ hoặc batch lên Kafka
- ✅ Hỗ trợ đa ngôn ngữ (Vietnamese, English)

### Worker Service
- ✅ Lắng nghe Kafka topic
- ✅ Xử lý embedding tự động
- ✅ Lưu trữ vào Qdrant theo collection (phân theo product_code)
- ✅ Batch processing để tối ưu hiệu suất
- ✅ Graceful shutdown

## Cài đặt

### Yêu cầu
- Docker & Docker Compose
- Python 3.11+ (nếu chạy local)

### Chạy với Docker Compose (Khuyến nghị)

```bash
# Clone repository
cd /root/develop/MISA.MIMOSAONLINE.AI

# Khởi động tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng services
docker-compose down
```

Services sẽ chạy trên:
- **API Service**: http://localhost:8000
- **Kafka**: localhost:9092
- **Qdrant**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### Chạy Local (Development)

#### 1. Khởi động infrastructure
```bash
docker-compose up -d zookeeper kafka qdrant
```

#### 2. Cài đặt API Service
```bash
cd api-service
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

#### 3. Cài đặt Worker Service
```bash
cd worker-service
pip install -r requirements.txt
cp .env.example .env
python -m app.kafka_consumer
```

## Sử dụng

### 1. Push dữ liệu để embedding

```bash
curl -X POST "http://localhost:8000/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### 2. Push batch dữ liệu

```bash
curl -X POST "http://localhost:8000/api/v1/push/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-123",
    "data_list": [
      {
        "accounting_object_id": "31731b46-f49e-4e07-a390-43cc3045d80a",
        "accounting_object_code": "ATM",
        "accounting_object_name": "Thu từ Dịch vụ thu hộ, chi hộ, ủy nhiệm thanh toán.",
        "address": "Lê Lợi - Sơn Tây - Hà Nội",
        "is_employee": false,
        "is_employee_outside": false,
        "inactive": false,
        "is_customer_vendor": false,
        "ihos_edit_version": 0,
        "receipt_amount": -140900000.0,
        "return_amount": -29580248.0
      }
    ]
  }'
```

### 3. Tìm kiếm ngữ nghĩa

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "công ty cấp nước",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-123",
    "limit": 10
  }'
```

Kết quả trả về:
```json
{
  "results": [
    {
      "score": 0.95,
      "metadata": {...},
      "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
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

## API Documentation

Sau khi khởi động API service, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Cấu trúc dữ liệu

### Accounting Object Model
```python
{
    "accounting_object_id": "UUID",
    "accounting_object_code": "string",
    "accounting_object_name": "string",  # Trường này được embedding
    "address": "string",
    "is_employee": bool,
    "is_employee_outside": bool,
    "inactive": bool,
    "is_customer_vendor": bool,
    "ihos_edit_version": int,
    "receipt_amount": float (optional),
    "return_amount": float (optional)
}
```

### Collection Structure
- Mỗi `product_code` có một collection riêng: `product_{product_code}`
- Dữ liệu được filter theo `tenant_id`
- Embedding được tạo từ `accounting_object_name`
- Metadata chứa toàn bộ thông tin của accounting object

## Embedding Model

Sử dụng model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Hỗ trợ đa ngôn ngữ (Vietnamese, English, etc.)
- Vector size: 384 dimensions
- Distance metric: Cosine similarity

## Monitoring

### Kiểm tra health
```bash
curl http://localhost:8000/health
```

### Xem Qdrant collections
```bash
curl http://localhost:6333/collections
```

### Kafka topics
```bash
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Troubleshooting

### Worker không nhận được messages
```bash
# Kiểm tra Kafka topic
docker exec -it kafka kafka-topics --describe --topic embedding-requests --bootstrap-server localhost:9092

# Kiểm tra consumer group
docker exec -it kafka kafka-consumer-groups --describe --group embedding-worker-group --bootstrap-server localhost:9092
```

### Qdrant connection issues
```bash
# Kiểm tra Qdrant health
curl http://localhost:6333/health

# Xem collections
curl http://localhost:6333/collections
```

## Development

### Cấu trúc thư mục
```
MISA.MIMOSAONLINE.AI/
├── api-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── kafka_producer.py
│   │   └── qdrant_service.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── worker-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── embedding_service.py
│   │   └── kafka_consumer.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── docker-compose.yml
└── README.md
```

## License

MIT License

## Support

Để được hỗ trợ, vui lòng tạo issue trên repository.

