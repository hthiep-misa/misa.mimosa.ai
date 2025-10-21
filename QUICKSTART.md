# Quick Start Guide

Hướng dẫn nhanh để chạy hệ thống Semantic Search.

## 🚀 Khởi động nhanh với Docker Compose

### Bước 1: Khởi động tất cả services

```bash
cd /root/develop/MISA.MIMOSAONLINE.AI
docker-compose up -d
```

Chờ khoảng 30-60 giây để tất cả services khởi động hoàn tất.

### Bước 2: Kiểm tra services đang chạy

```bash
docker-compose ps
```

Bạn sẽ thấy 5 services:
- `zookeeper` - Kafka coordinator
- `kafka` - Message broker
- `qdrant` - Vector database
- `api-service` - FastAPI REST API
- `worker-service` - Embedding worker

### Bước 3: Kiểm tra health

```bash
curl http://localhost:8000/health
```

Kết quả:
```json
{
  "message": "Service is healthy",
  "status": "success"
}
```

### Bước 4: Chạy test script

```bash
python3 test_example.py
```

Script này sẽ:
1. ✅ Kiểm tra health của API
2. ✅ Push 5 bản ghi mẫu lên Kafka
3. ✅ Đợi worker xử lý embedding
4. ✅ Thực hiện 5 truy vấn tìm kiếm khác nhau

## 📝 Sử dụng API

### 1. Push dữ liệu đơn lẻ

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

### 2. Tìm kiếm ngữ nghĩa

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

### 3. Push batch dữ liệu

Xem file `test_example.py` để biết cách push batch data.

## 🔍 Monitoring

### Xem logs của API service
```bash
docker-compose logs -f api-service
```

### Xem logs của Worker service
```bash
docker-compose logs -f worker-service
```

### Truy cập Qdrant Dashboard
Mở browser: http://localhost:6333/dashboard

### Xem API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛑 Dừng services

```bash
docker-compose down
```

Để xóa cả volumes (dữ liệu):
```bash
docker-compose down -v
```

## 🔧 Troubleshooting

### Lỗi: Port đã được sử dụng

Nếu port 8000, 9092, hoặc 6333 đã được sử dụng, edit file `docker-compose.yml` để đổi port.

### Worker không xử lý messages

1. Kiểm tra Kafka đang chạy:
```bash
docker-compose logs kafka
```

2. Kiểm tra worker logs:
```bash
docker-compose logs worker-service
```

3. Restart worker:
```bash
docker-compose restart worker-service
```

### Không tìm thấy kết quả

1. Đảm bảo đã push data trước
2. Đợi 5-10 giây để worker xử lý
3. Kiểm tra `product_code` và `tenant_id` khớp với data đã push

## 📊 Ví dụ tìm kiếm

Sau khi push dữ liệu mẫu, bạn có thể thử các truy vấn:

1. **Tìm công ty cấp nước:**
   - Query: "công ty cấp nước"
   - Kết quả: Công ty cổ phần cấp nước Sơn Tây

2. **Tìm bảo hiểm:**
   - Query: "bảo hiểm xã hội"
   - Kết quả: Bảo hiểm xã hội Sơn Tây - Hà Nội

3. **Tìm bưu điện:**
   - Query: "bưu điện"
   - Kết quả: Bưu điện thị xã Sơn Tây

4. **Tìm UBND:**
   - Query: "UBND phường"
   - Kết quả: UBND PHƯỜNG LÊ LỢI

5. **Tìm dịch vụ:**
   - Query: "dịch vụ thu hộ"
   - Kết quả: Thu từ Dịch vụ thu hộ, chi hộ, ủy nhiệm thanh toán.

## 🎯 Các tính năng chính

✅ **Tìm kiếm ngữ nghĩa**: Tìm theo ý nghĩa, không cần khớp chính xác từ khóa

✅ **Đa ngôn ngữ**: Hỗ trợ tiếng Việt và tiếng Anh

✅ **Multi-tenant**: Phân tách dữ liệu theo tenant_id

✅ **Collection theo product**: Mỗi product_code có collection riêng

✅ **Batch processing**: Xử lý hàng loạt để tối ưu hiệu suất

✅ **Scalable**: Có thể scale worker để xử lý nhiều messages hơn

## 💡 Tips

1. **Tối ưu tìm kiếm**: Sử dụng câu truy vấn ngắn gọn, tập trung vào từ khóa chính

2. **Batch push**: Khi có nhiều dữ liệu, sử dụng `/api/v1/push/batch` thay vì push từng bản ghi

3. **Monitoring**: Thường xuyên kiểm tra logs để phát hiện lỗi sớm

4. **Backup**: Qdrant data được lưu trong Docker volume `qdrant_storage`

## 📚 Tài liệu chi tiết

- [README.md](README.md) - Tài liệu đầy đủ
- [API Service README](api-service/README.md) - Chi tiết về API
- [Worker Service README](worker-service/README.md) - Chi tiết về Worker

## 🆘 Cần trợ giúp?

Nếu gặp vấn đề, hãy:
1. Kiểm tra logs của service bị lỗi
2. Xem phần Troubleshooting ở trên
3. Đọc tài liệu chi tiết trong README.md

