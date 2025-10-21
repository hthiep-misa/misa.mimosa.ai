# API Documentation

## Tổng quan

API Service cung cấp các endpoint để tìm kiếm ngữ nghĩa (semantic search) và đẩy dữ liệu vào hàng đợi để xử lý embedding. Service sử dụng QdrantDB để lưu trữ vector embeddings và Apache Kafka để xử lý bất đồng bộ.

**Base URL**: `http://localhost:8000`

**Version**: 1.0.0

---

## Endpoints

### 1. Root Endpoint

**GET** `/`

Kiểm tra trạng thái API và xem danh sách các endpoint có sẵn.

#### Response

```json
{
  "message": "Semantic Search API is running",
  "status": "success",
  "details": {
    "version": "1.0.0",
    "endpoints": {
      "search": "/api/v1/search",
      "push": "/api/v1/push",
      "push_batch": "/api/v1/push/batch"
    }
  }
}
```

---

### 2. Health Check

**GET** `/health`

Kiểm tra sức khỏe của service.

#### Response

```json
{
  "message": "Service is healthy",
  "status": "success"
}
```

---

### 3. Semantic Search

**POST** `/api/v1/search`

Tìm kiếm đối tượng kế toán theo ngữ nghĩa dựa trên query text.

#### Request Body

```json
{
  "query": "công ty cấp nước",
  "product_code": "PRODUCT_001",
  "tenant_id": "TENANT_001",
  "limit": 10
}
```

#### Request Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Câu truy vấn tìm kiếm (tiếng Việt hoặc tiếng Anh) |
| `product_code` | string | ✅ Yes | - | Mã sản phẩm để lọc collection |
| `tenant_id` | string | ✅ Yes | - | Mã tenant để lọc kết quả |
| `limit` | integer | ❌ No | 10 | Số lượng kết quả trả về (1-100) |

#### Response

```json
{
  "results": [
    {
      "score": 0.8934,
      "metadata": {
        "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
        "accounting_object_code": "CTCPCNST",
        "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
        "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
        "is_employee": false,
        "is_employee_outside": false,
        "inactive": false,
        "is_customer_vendor": false,
        "ihos_edit_version": 0,
        "tenant_id": "TENANT_001"
      },
      "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
      "accounting_object_code": "CTCPCNST",
      "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
      "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội"
    }
  ],
  "total": 1,
  "query": "công ty cấp nước",
  "product_code": "PRODUCT_001",
  "tenant_id": "TENANT_001"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Danh sách kết quả tìm kiếm |
| `results[].score` | float | Điểm tương đồng (0.0 - 1.0, càng cao càng giống) |
| `results[].metadata` | object | Toàn bộ metadata của đối tượng |
| `results[].accounting_object_id` | UUID | ID của đối tượng kế toán |
| `results[].accounting_object_code` | string | Mã đối tượng kế toán |
| `results[].accounting_object_name` | string | Tên đối tượng kế toán |
| `results[].address` | string | Địa chỉ |
| `total` | integer | Tổng số kết quả trả về |
| `query` | string | Query đã tìm kiếm |
| `product_code` | string | Product code đã lọc |
| `tenant_id` | string | Tenant ID đã lọc |

#### Error Response

```json
{
  "detail": "Search failed: Collection not found"
}
```

**Status Codes:**
- `200 OK`: Tìm kiếm thành công
- `500 Internal Server Error`: Lỗi server hoặc Qdrant không khả dụng

---

### 4. Push Data for Embedding

**POST** `/api/v1/push`

Đẩy một đối tượng kế toán vào Kafka queue để worker xử lý embedding và lưu vào Qdrant.

#### Request Body

```json
{
  "product_code": "PRODUCT_001",
  "tenant_id": "TENANT_001",
  "data": {
    "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
    "accounting_object_code": "CTCPCNST",
    "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
    "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
    "is_employee": false,
    "is_employee_outside": false,
    "inactive": false,
    "is_customer_vendor": false,
    "ihos_edit_version": 0,
    "receipt_amount": 1000000.0,
    "return_amount": 500000.0
  },
  "metadata": {
    "source": "api",
    "timestamp": "2025-10-21T10:30:00Z"
  }
}
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_code` | string | ✅ Yes | Mã sản phẩm (dùng làm tên collection trong Qdrant) |
| `tenant_id` | string | ✅ Yes | Mã tenant |
| `data` | object | ✅ Yes | Đối tượng kế toán cần embedding |
| `data.accounting_object_id` | UUID | ✅ Yes | ID duy nhất của đối tượng |
| `data.accounting_object_code` | string | ✅ Yes | Mã đối tượng |
| `data.accounting_object_name` | string | ✅ Yes | Tên đối tượng (sẽ được embedding) |
| `data.address` | string | ❌ No | Địa chỉ |
| `data.is_employee` | boolean | ❌ No | Có phải nhân viên không |
| `data.is_employee_outside` | boolean | ❌ No | Có phải nhân viên bên ngoài không |
| `data.inactive` | boolean | ❌ No | Trạng thái không hoạt động |
| `data.is_customer_vendor` | boolean | ❌ No | Có phải khách hàng/nhà cung cấp không |
| `data.ihos_edit_version` | integer | ❌ No | Phiên bản chỉnh sửa |
| `data.receipt_amount` | float | ❌ No | Số tiền thu |
| `data.return_amount` | float | ❌ No | Số tiền trả |
| `metadata` | object | ❌ No | Metadata bổ sung (tùy chọn) |

#### Response

```json
{
  "message": "Data pushed to processing queue successfully",
  "status": "success",
  "details": {
    "product_code": "PRODUCT_001",
    "tenant_id": "TENANT_001",
    "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf"
  }
}
```

#### Error Response

```json
{
  "detail": "Failed to send message to Kafka"
}
```

**Status Codes:**
- `200 OK`: Đẩy dữ liệu thành công
- `500 Internal Server Error`: Lỗi kết nối Kafka hoặc lỗi server

---

### 5. Push Batch Data for Embedding

**POST** `/api/v1/push/batch`

Đẩy nhiều đối tượng kế toán cùng lúc vào Kafka queue để xử lý hàng loạt.

#### Request Body

```json
{
  "product_code": "PRODUCT_001",
  "tenant_id": "TENANT_001",
  "data_list": [
    {
      "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
      "accounting_object_code": "CTCPCNST",
      "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
      "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
      "is_employee": false,
      "is_employee_outside": false,
      "inactive": false,
      "is_customer_vendor": false,
      "ihos_edit_version": 0
    },
    {
      "accounting_object_id": "31731b46-f49e-4e07-a390-43cc3045d80a",
      "accounting_object_code": "ATM",
      "accounting_object_name": "Thu từ Dịch vụ thu hộ, chi hộ, ủy nhiệm thanh toán.",
      "address": "Lê Lợi - Sơn Tây - Hà Nội",
      "is_employee": false,
      "is_employee_outside": false,
      "inactive": false,
      "is_customer_vendor": false,
      "ihos_edit_version": 0
    }
  ]
}
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_code` | string | ✅ Yes | Mã sản phẩm |
| `tenant_id` | string | ✅ Yes | Mã tenant |
| `data_list` | array | ✅ Yes | Danh sách các đối tượng kế toán (cấu trúc giống `/api/v1/push`) |

#### Response

```json
{
  "message": "Batch push completed",
  "status": "success",
  "details": {
    "product_code": "PRODUCT_001",
    "tenant_id": "TENANT_001",
    "total": 2,
    "success": 2,
    "failed": 0
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `details.total` | integer | Tổng số bản ghi được gửi |
| `details.success` | integer | Số bản ghi gửi thành công |
| `details.failed` | integer | Số bản ghi gửi thất bại |

**Status Codes:**
- `200 OK`: Hoàn thành batch push (kiểm tra `success`/`failed` để biết chi tiết)
- `500 Internal Server Error`: Lỗi server

---

## Cách sử dụng

### 1. Khởi động services

```bash
# Khởi động infrastructure (Qdrant + Kafka)
cd /root/develop/MISA.MIMOSAONLINE.AI
make up

# Khởi động API service
cd api-service
make setup    # Lần đầu tiên
make run      # Chạy service

# Khởi động Worker service (terminal khác)
cd worker-service
make setup    # Lần đầu tiên
make run      # Chạy worker
```

### 2. Push dữ liệu để embedding

**Ví dụ 1: Push một bản ghi**

```bash
curl -X POST "http://localhost:8000/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "MIMOSA_ACCOUNTING",
    "tenant_id": "TENANT_DEMO",
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

**Ví dụ 2: Push batch nhiều bản ghi**

```bash
curl -X POST "http://localhost:8000/api/v1/push/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "MIMOSA_ACCOUNTING",
    "tenant_id": "TENANT_DEMO",
    "data_list": [
      {
        "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
        "accounting_object_code": "CTCPCNST",
        "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
        "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
        "is_employee": false,
        "is_employee_outside": false,
        "inactive": false,
        "is_customer_vendor": false,
        "ihos_edit_version": 0
      },
      {
        "accounting_object_id": "31731b46-f49e-4e07-a390-43cc3045d80a",
        "accounting_object_code": "ATM",
        "accounting_object_name": "Thu từ Dịch vụ thu hộ, chi hộ, ủy nhiệm thanh toán",
        "address": "Lê Lợi - Sơn Tây - Hà Nội",
        "is_employee": false,
        "is_employee_outside": false,
        "inactive": false,
        "is_customer_vendor": false,
        "ihos_edit_version": 0
      }
    ]
  }'
```

### 3. Tìm kiếm ngữ nghĩa

**Ví dụ 1: Tìm kiếm công ty cấp nước**

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "công ty cấp nước",
    "product_code": "MIMOSA_ACCOUNTING",
    "tenant_id": "TENANT_DEMO",
    "limit": 10
  }'
```

**Ví dụ 2: Tìm kiếm bưu điện**

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bưu điện",
    "product_code": "MIMOSA_ACCOUNTING",
    "tenant_id": "TENANT_DEMO",
    "limit": 5
  }'
```

**Ví dụ 3: Tìm kiếm bảo hiểm xã hội**

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bảo hiểm xã hội",
    "product_code": "MIMOSA_ACCOUNTING",
    "tenant_id": "TENANT_DEMO",
    "limit": 10
  }'
```

### 4. Sử dụng với Python

**Cài đặt thư viện:**

```bash
pip install requests
```

**Code mẫu:**

```python
import requests
import json

API_URL = "http://localhost:8000"

# 1. Push data
def push_data(product_code, tenant_id, data):
    response = requests.post(
        f"{API_URL}/api/v1/push",
        json={
            "product_code": product_code,
            "tenant_id": tenant_id,
            "data": data
        }
    )
    return response.json()

# 2. Search
def search(query, product_code, tenant_id, limit=10):
    response = requests.post(
        f"{API_URL}/api/v1/search",
        json={
            "query": query,
            "product_code": product_code,
            "tenant_id": tenant_id,
            "limit": limit
        }
    )
    return response.json()

# Ví dụ sử dụng
if __name__ == "__main__":
    # Push data
    data = {
        "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
        "accounting_object_code": "CTCPCNST",
        "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
        "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
        "is_employee": False,
        "is_employee_outside": False,
        "inactive": False,
        "is_customer_vendor": False,
        "ihos_edit_version": 0
    }
    
    result = push_data("MIMOSA_ACCOUNTING", "TENANT_DEMO", data)
    print("Push result:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # Wait for worker to process (a few seconds)
    import time
    time.sleep(3)
    
    # Search
    results = search("công ty cấp nước", "MIMOSA_ACCOUNTING", "TENANT_DEMO")
    print("\nSearch results:", json.dumps(results, indent=2, ensure_ascii=False))
```

### 5. Sử dụng với JavaScript/TypeScript

```javascript
const API_URL = "http://localhost:8000";

// 1. Push data
async function pushData(productCode, tenantId, data) {
  const response = await fetch(`${API_URL}/api/v1/push`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      product_code: productCode,
      tenant_id: tenantId,
      data: data
    })
  });
  return await response.json();
}

// 2. Search
async function search(query, productCode, tenantId, limit = 10) {
  const response = await fetch(`${API_URL}/api/v1/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: query,
      product_code: productCode,
      tenant_id: tenantId,
      limit: limit
    })
  });
  return await response.json();
}

// Ví dụ sử dụng
(async () => {
  // Push data
  const data = {
    accounting_object_id: "2966398d-f24d-450f-a9c9-bffde6c2aadf",
    accounting_object_code: "CTCPCNST",
    accounting_object_name: "Công ty cổ phần cấp nước Sơn Tây",
    address: "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội",
    is_employee: false,
    is_employee_outside: false,
    inactive: false,
    is_customer_vendor: false,
    ihos_edit_version: 0
  };
  
  const pushResult = await pushData("MIMOSA_ACCOUNTING", "TENANT_DEMO", data);
  console.log("Push result:", pushResult);
  
  // Wait for worker to process
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Search
  const searchResults = await search("công ty cấp nước", "MIMOSA_ACCOUNTING", "TENANT_DEMO");
  console.log("Search results:", searchResults);
})();
```

---

## Luồng xử lý dữ liệu

```
┌──────────┐         ┌──────────┐         ┌────────┐         ┌─────────┐
│  Client  │────────>│   API    │────────>│ Kafka  │────────>│ Worker  │
│          │  POST   │ Service  │  Push   │ Queue  │ Consume │ Service │
└──────────┘  /push  └──────────┘         └────────┘         └─────────┘
                                                                    │
                                                                    │ Embed
                                                                    │ + Store
                                                                    ▼
┌──────────┐         ┌──────────┐                            ┌─────────┐
│  Client  │────────>│   API    │───────────────────────────>│ Qdrant  │
│          │  POST   │ Service  │  Query Vector Similarity   │   DB    │
└──────────┘ /search └──────────┘<───────────────────────────└─────────┘
                                      Return Results
```

### Các bước:

1. **Push Data** (`/api/v1/push`):
   - Client gửi dữ liệu đối tượng kế toán
   - API Service đẩy message vào Kafka queue
   - Trả về response ngay lập tức (async)

2. **Worker Processing**:
   - Worker service lắng nghe Kafka queue
   - Nhận message và embedding `accounting_object_name`
   - Lưu vector + metadata vào Qdrant DB
   - Collection được tổ chức theo `product_code`

3. **Search** (`/api/v1/search`):
   - Client gửi query text
   - API Service embedding query text
   - Tìm kiếm vector tương đồng trong Qdrant
   - Lọc theo `product_code` và `tenant_id`
   - Trả về top N kết quả có điểm cao nhất

---

## Lưu ý quan trọng

### 1. Product Code & Tenant ID

- **`product_code`**: Dùng để phân chia collections trong Qdrant. Mỗi product code sẽ có một collection riêng.
- **`tenant_id`**: Dùng để lọc dữ liệu trong cùng một collection, hỗ trợ multi-tenancy.

**Ví dụ:**
- `product_code = "MIMOSA_ACCOUNTING"` → Collection: `mimosa_accounting`
- `tenant_id = "TENANT_001"` → Filter trong collection

### 2. Embedding Model

Service sử dụng model **`keepitreal/vietnamese-sbert`** (PhoBERT-based):
- Vector size: **768 dimensions**
- Tối ưu cho tiếng Việt
- Độ chính xác cao cho semantic search

### 3. Thời gian xử lý

- **Push API**: Trả về ngay (~10-50ms)
- **Worker processing**: 1-3 giây/bản ghi (tùy thuộc vào độ dài text)
- **Search API**: 50-200ms (tùy thuộc vào số lượng vectors trong collection)

### 4. Giới hạn

- **Search limit**: 1-100 kết quả
- **Batch push**: Không giới hạn số lượng, nhưng nên push <= 1000 bản ghi/lần
- **Query length**: Không giới hạn, nhưng nên <= 512 tokens

### 5. Error Handling

Tất cả các endpoint đều trả về error với format:

```json
{
  "detail": "Error message here"
}
```

**Common errors:**
- `Collection not found`: Chưa có dữ liệu cho `product_code` này
- `Failed to send message to Kafka`: Kafka không khả dụng
- `Search failed`: Qdrant không khả dụng hoặc lỗi query

---

## Swagger UI

API cung cấp interactive documentation tại:

**URL**: `http://localhost:8000/docs`

Tại đây bạn có thể:
- Xem chi tiết tất cả các endpoints
- Test API trực tiếp từ browser
- Xem request/response schemas
- Download OpenAPI specification

---

## Monitoring & Logs

### API Service Logs

```bash
cd api-service
make logs
```

### Worker Service Logs

Worker service có log format đẹp với màu sắc:

```bash
cd worker-service
make run
```

**Log format:**
```
2025-10-21 10:30:45 INFO     [consumer] 🔄 Processing batch: 5 messages
2025-10-21 10:30:46 INFO     [embedding] ✅ Stored: CTCPCNST → mimosa_accounting
```

---

## Troubleshooting

### 1. Không tìm thấy kết quả

**Nguyên nhân:**
- Chưa push dữ liệu
- Worker chưa xử lý xong
- Sai `product_code` hoặc `tenant_id`

**Giải pháp:**
```bash
# Kiểm tra worker logs
cd worker-service
make logs

# Kiểm tra Qdrant collections
curl http://localhost:6333/collections
```

### 2. Push data thất bại

**Nguyên nhân:**
- Kafka không chạy
- Sai format dữ liệu

**Giải pháp:**
```bash
# Kiểm tra Kafka
make status

# Restart Kafka
make restart-kafka
```

### 3. Search chậm

**Nguyên nhân:**
- Quá nhiều vectors trong collection
- Qdrant chưa được optimize

**Giải pháp:**
- Tăng resources cho Qdrant
- Sử dụng `limit` nhỏ hơn
- Tạo indexes trong Qdrant

---

## Tài liệu liên quan

- [QUICKSTART.md](./QUICKSTART.md) - Hướng dẫn bắt đầu nhanh
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Kiến trúc hệ thống
- [EXAMPLES.md](./EXAMPLES.md) - Các ví dụ chi tiết
- [CHEATSHEET.md](./CHEATSHEET.md) - Các lệnh thường dùng

---

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs của API và Worker service
2. Xem [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Tạo issue trên GitHub repository

