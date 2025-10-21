# Ví dụ sử dụng

Tài liệu này cung cấp các ví dụ chi tiết về cách sử dụng hệ thống Semantic Search.

## Mục lục
1. [Khởi động hệ thống](#1-khởi-động-hệ-thống)
2. [Push dữ liệu](#2-push-dữ-liệu)
3. [Tìm kiếm](#3-tìm-kiếm)
4. [Sử dụng với Python](#4-sử-dụng-với-python)
5. [Sử dụng với JavaScript](#5-sử-dụng-với-javascript)
6. [Best Practices](#6-best-practices)

## 1. Khởi động hệ thống

### Sử dụng Docker Compose

```bash
# Di chuyển vào thư mục project
cd /root/develop/MISA.MIMOSAONLINE.AI

# Khởi động tất cả services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps

# Xem logs
docker-compose logs -f api-service
docker-compose logs -f worker-service
```

### Kiểm tra health

```bash
curl http://localhost:8000/health
```

## 2. Push dữ liệu

### 2.1. Push một bản ghi

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
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

**Response:**
```json
{
  "message": "Data pushed to processing queue successfully",
  "status": "success",
  "details": {
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf"
  }
}
```

### 2.2. Push nhiều bản ghi (Batch)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/push/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
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
      },
      {
        "accounting_object_id": "3324977b-e614-4ada-897b-d74a81883240",
        "accounting_object_code": "BẢO HIỂM",
        "accounting_object_name": "Bảo hiểm xã hội Sơn Tây - Hà Nội",
        "address": "Đường La Thành- Phú Thịnh - Sơn Tây - Hà Nội",
        "is_employee": false,
        "is_employee_outside": false,
        "inactive": false,
        "is_customer_vendor": false,
        "ihos_edit_version": 0,
        "receipt_amount": 17800000.0
      }
    ]
  }'
```

**Response:**
```json
{
  "message": "Batch push completed",
  "status": "success",
  "details": {
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "total": 2,
    "success": 2,
    "failed": 0
  }
}
```

### 2.3. Push với metadata tùy chỉnh

```bash
curl -X POST "http://localhost:8000/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
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
    },
    "metadata": {
      "source": "import_2024",
      "category": "water_company",
      "priority": "high"
    }
  }'
```

## 3. Tìm kiếm

### 3.1. Tìm kiếm cơ bản

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "công ty cấp nước",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 10
  }'
```

**Response:**
```json
{
  "results": [
    {
      "score": 0.9523,
      "metadata": {
        "tenant_id": "tenant-001",
        "product_code": "ACCOUNTING",
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
      "accounting_object_id": "2966398d-f24d-450f-a9c9-bffde6c2aadf",
      "accounting_object_code": "CTCPCNST",
      "accounting_object_name": "Công ty cổ phần cấp nước Sơn Tây",
      "address": "Số 193 Lê Lợi, thị xã Sơn Tây, Hà Nội"
    }
  ],
  "total": 1,
  "query": "công ty cấp nước",
  "product_code": "ACCOUNTING",
  "tenant_id": "tenant-001"
}
```

### 3.2. Các ví dụ tìm kiếm khác nhau

#### Tìm bảo hiểm xã hội
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bảo hiểm xã hội",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 5
  }'
```

#### Tìm bưu điện
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bưu điện",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 5
  }'
```

#### Tìm UBND
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "UBND phường",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 5
  }'
```

#### Tìm dịch vụ
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "dịch vụ thu hộ chi hộ",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 5
  }'
```

### 3.3. Tìm kiếm với limit khác nhau

```bash
# Top 3 kết quả
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "công ty",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 3
  }'

# Top 20 kết quả
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "công ty",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 20
  }'
```

## 4. Sử dụng với Python

### 4.1. Cài đặt

```bash
pip install requests
```

### 4.2. Push dữ liệu

```python
import requests
import json

API_URL = "http://localhost:8000"

def push_accounting_object(product_code, tenant_id, data):
    """Push một accounting object"""
    url = f"{API_URL}/api/v1/push"
    payload = {
        "product_code": product_code,
        "tenant_id": tenant_id,
        "data": data
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Sử dụng
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

result = push_accounting_object("ACCOUNTING", "tenant-001", data)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 4.3. Push batch

```python
def push_batch(product_code, tenant_id, data_list):
    """Push nhiều accounting objects"""
    url = f"{API_URL}/api/v1/push/batch"
    payload = {
        "product_code": product_code,
        "tenant_id": tenant_id,
        "data_list": data_list
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Sử dụng
data_list = [
    {
        "accounting_object_id": "id-1",
        "accounting_object_code": "CODE1",
        "accounting_object_name": "Công ty A",
        # ... other fields
    },
    {
        "accounting_object_id": "id-2",
        "accounting_object_code": "CODE2",
        "accounting_object_name": "Công ty B",
        # ... other fields
    }
]

result = push_batch("ACCOUNTING", "tenant-001", data_list)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 4.4. Tìm kiếm

```python
def search(query, product_code, tenant_id, limit=10):
    """Tìm kiếm semantic"""
    url = f"{API_URL}/api/v1/search"
    payload = {
        "query": query,
        "product_code": product_code,
        "tenant_id": tenant_id,
        "limit": limit
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Sử dụng
results = search("công ty cấp nước", "ACCOUNTING", "tenant-001", limit=5)

print(f"Tìm thấy {results['total']} kết quả:")
for i, result in enumerate(results['results'], 1):
    print(f"\n{i}. {result['accounting_object_name']}")
    print(f"   Score: {result['score']:.4f}")
    print(f"   Code: {result['accounting_object_code']}")
    print(f"   Address: {result.get('address', 'N/A')}")
```

### 4.5. Class wrapper hoàn chỉnh

```python
import requests
from typing import List, Dict, Any, Optional

class SemanticSearchClient:
    """Client để tương tác với Semantic Search API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """Kiểm tra health của service"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def push(
        self,
        product_code: str,
        tenant_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Push một bản ghi"""
        payload = {
            "product_code": product_code,
            "tenant_id": tenant_id,
            "data": data,
            "metadata": metadata or {}
        }
        response = requests.post(f"{self.base_url}/api/v1/push", json=payload)
        response.raise_for_status()
        return response.json()
    
    def push_batch(
        self,
        product_code: str,
        tenant_id: str,
        data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Push nhiều bản ghi"""
        payload = {
            "product_code": product_code,
            "tenant_id": tenant_id,
            "data_list": data_list
        }
        response = requests.post(f"{self.base_url}/api/v1/push/batch", json=payload)
        response.raise_for_status()
        return response.json()
    
    def search(
        self,
        query: str,
        product_code: str,
        tenant_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Tìm kiếm semantic"""
        payload = {
            "query": query,
            "product_code": product_code,
            "tenant_id": tenant_id,
            "limit": limit
        }
        response = requests.post(f"{self.base_url}/api/v1/search", json=payload)
        response.raise_for_status()
        return response.json()

# Sử dụng
client = SemanticSearchClient()

# Health check
print(client.health_check())

# Push data
result = client.push("ACCOUNTING", "tenant-001", {...})

# Search
results = client.search("công ty cấp nước", "ACCOUNTING", "tenant-001")
```

## 5. Sử dụng với JavaScript

### 5.1. Sử dụng fetch API

```javascript
const API_URL = 'http://localhost:8000';

// Push dữ liệu
async function pushData(productCode, tenantId, data) {
  const response = await fetch(`${API_URL}/api/v1/push`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      product_code: productCode,
      tenant_id: tenantId,
      data: data
    })
  });
  
  return await response.json();
}

// Tìm kiếm
async function search(query, productCode, tenantId, limit = 10) {
  const response = await fetch(`${API_URL}/api/v1/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      product_code: productCode,
      tenant_id: tenantId,
      limit: limit
    })
  });
  
  return await response.json();
}

// Sử dụng
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

// Push
pushData("ACCOUNTING", "tenant-001", data)
  .then(result => console.log(result));

// Search
search("công ty cấp nước", "ACCOUNTING", "tenant-001", 10)
  .then(results => {
    console.log(`Found ${results.total} results:`);
    results.results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.accounting_object_name} (Score: ${result.score})`);
    });
  });
```

### 5.2. Class wrapper với axios

```javascript
const axios = require('axios');

class SemanticSearchClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
  
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
  
  async push(productCode, tenantId, data, metadata = {}) {
    const response = await this.client.post('/api/v1/push', {
      product_code: productCode,
      tenant_id: tenantId,
      data: data,
      metadata: metadata
    });
    return response.data;
  }
  
  async pushBatch(productCode, tenantId, dataList) {
    const response = await this.client.post('/api/v1/push/batch', {
      product_code: productCode,
      tenant_id: tenantId,
      data_list: dataList
    });
    return response.data;
  }
  
  async search(query, productCode, tenantId, limit = 10) {
    const response = await this.client.post('/api/v1/search', {
      query: query,
      product_code: productCode,
      tenant_id: tenantId,
      limit: limit
    });
    return response.data;
  }
}

// Sử dụng
const client = new SemanticSearchClient();

(async () => {
  // Health check
  const health = await client.healthCheck();
  console.log(health);
  
  // Search
  const results = await client.search('công ty cấp nước', 'ACCOUNTING', 'tenant-001');
  console.log(results);
})();
```

## 6. Best Practices

### 6.1. Tối ưu tìm kiếm

✅ **DO:**
- Sử dụng câu truy vấn ngắn gọn, tập trung
- Bao gồm từ khóa chính
- Sử dụng ngôn ngữ tự nhiên

❌ **DON'T:**
- Truy vấn quá dài, phức tạp
- Chỉ sử dụng 1 từ quá chung chung
- Sử dụng ký tự đặc biệt không cần thiết

**Ví dụ:**
```
✅ Good: "công ty cấp nước"
✅ Good: "bảo hiểm xã hội"
❌ Bad: "công ty"
❌ Bad: "tìm kiếm tất cả các công ty cổ phần hoạt động trong lĩnh vực cấp nước"
```

### 6.2. Batch processing

Khi có nhiều dữ liệu, sử dụng batch API:

```python
# ✅ Good - Batch
client.push_batch("ACCOUNTING", "tenant-001", [data1, data2, data3, ...])

# ❌ Bad - Multiple single pushes
for data in data_list:
    client.push("ACCOUNTING", "tenant-001", data)
```

### 6.3. Error handling

Luôn xử lý errors:

```python
try:
    results = client.search(query, product_code, tenant_id)
    if results['total'] == 0:
        print("Không tìm thấy kết quả")
    else:
        # Process results
        pass
except requests.exceptions.ConnectionError:
    print("Không thể kết nối đến API")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### 6.4. Timeout và retry

```python
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Sử dụng
session = create_session_with_retry()
response = session.post(url, json=payload, timeout=10)
```

### 6.5. Caching results

```python
from functools import lru_cache
import hashlib
import json

@lru_cache(maxsize=100)
def search_cached(query, product_code, tenant_id, limit):
    """Search with caching"""
    return client.search(query, product_code, tenant_id, limit)

# Sử dụng
results = search_cached("công ty cấp nước", "ACCOUNTING", "tenant-001", 10)
```

### 6.6. Monitoring

Log tất cả requests:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_with_logging(query, product_code, tenant_id, limit=10):
    logger.info(f"Searching: query={query}, product={product_code}, tenant={tenant_id}")
    
    start_time = time.time()
    results = client.search(query, product_code, tenant_id, limit)
    elapsed = time.time() - start_time
    
    logger.info(f"Search completed in {elapsed:.2f}s, found {results['total']} results")
    return results
```

## Tổng kết

Hệ thống Semantic Search cung cấp:
- ✅ API đơn giản, dễ sử dụng
- ✅ Tìm kiếm theo ngữ nghĩa, không cần khớp chính xác
- ✅ Hỗ trợ đa ngôn ngữ
- ✅ Multi-tenant
- ✅ Batch processing
- ✅ Scalable và performant

Tham khảo thêm:
- [README.md](README.md) - Tài liệu tổng quan
- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn nhanh
- [ARCHITECTURE.md](ARCHITECTURE.md) - Kiến trúc hệ thống

