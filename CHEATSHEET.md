# Cheatsheet - Các lệnh thường dùng

## 🚀 Quick Start (3 bước)

```bash
# 1. Start infrastructure
docker-compose up -d kafka qdrant

# 2. Setup API Service (Terminal 1)
cd api-service && make setup && make run

# 3. Setup Worker Service (Terminal 2)  
cd worker-service && make setup && make run
```

## 📦 API Service Commands

```bash
cd api-service

# Setup
make setup              # Setup hoàn chỉnh (lần đầu)
make venv               # Chỉ tạo venv
make install            # Cài dependencies

# Run
make run                # Chạy API
make dev                # Chạy với auto-reload

# Info
make help               # Xem tất cả commands
make info               # Xem thông tin environment
make check-infra        # Kiểm tra Kafka & Qdrant

# Development
make lint               # Check code style
make format             # Format code

# Cleanup
make clean              # Xóa venv
make clean-all          # Xóa venv + cache

# Manual
source .venv/bin/activate    # Activate venv
python -m app.main           # Run manually
deactivate                   # Deactivate venv
```

## 🔧 Worker Service Commands

```bash
cd worker-service

# Setup
make setup              # Setup hoàn chỉnh (lần đầu, mất vài phút)
make venv               # Chỉ tạo venv
make install            # Cài dependencies + download model
make download-model     # Download model riêng

# Run
make run                # Chạy worker
make dev                # Chạy với DEBUG logging

# Info
make help               # Xem tất cả commands
make info               # Xem thông tin environment
make check-infra        # Kiểm tra Kafka & Qdrant

# Development
make lint               # Check code style
make format             # Format code

# Cleanup
make clean              # Xóa venv
make clean-all          # Xóa venv + cache

# Manual
source .venv/bin/activate    # Activate venv
python -m app.kafka_consumer # Run manually
deactivate                   # Deactivate venv
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d kafka qdrant
docker-compose up -d api-service
docker-compose up -d worker-service

# View logs
docker-compose logs -f
docker-compose logs -f api-service
docker-compose logs -f worker-service

# Status
docker-compose ps

# Stop
docker-compose down

# Stop + remove volumes
docker-compose down -v

# Restart
docker-compose restart
docker-compose restart api-service
docker-compose restart worker-service
```

## 🧪 Testing

```bash
# Run test script
python3 test_example.py

# Health check
curl http://localhost:8000/health

# Push single data
curl -X POST "http://localhost:8000/api/v1/push" \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "data": {
      "accounting_object_id": "123",
      "accounting_object_code": "TEST",
      "accounting_object_name": "Test Company",
      "is_employee": false,
      "is_employee_outside": false,
      "inactive": false,
      "is_customer_vendor": false,
      "ihos_edit_version": 0
    }
  }'

# Search
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test company",
    "product_code": "ACCOUNTING",
    "tenant_id": "tenant-001",
    "limit": 10
  }'
```

## 🔍 Debugging

```bash
# Check infrastructure
cd api-service && make check-infra

# Check Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Check Kafka consumer groups
docker exec -it kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# Check Qdrant collections
curl http://localhost:6333/collections

# Check Qdrant health
curl http://localhost:6333/health

# View API logs (venv)
cd api-service && make dev

# View Worker logs (venv)
cd worker-service && make dev

# View Docker logs
docker-compose logs -f api-service
docker-compose logs -f worker-service
```

## 🛠️ Development Workflow

```bash
# 1. Start infrastructure
docker-compose up -d kafka qdrant

# 2. Terminal 1 - API
cd api-service
make dev

# 3. Terminal 2 - Worker
cd worker-service
make dev

# 4. Terminal 3 - Testing
python3 test_example.py

# 5. Make changes to code

# 6. API auto-reloads, Worker needs restart
# Press Ctrl+C in Worker terminal, then:
make dev
```

## 📝 Configuration

```bash
# API Service config
cd api-service
nano .env

# Worker Service config
cd worker-service
nano .env

# Docker Compose config
nano docker-compose.yml
```

## 🧹 Cleanup

```bash
# Clean API venv
cd api-service && make clean-all

# Clean Worker venv
cd worker-service && make clean-all

# Clean Docker
docker-compose down -v

# Clean everything
cd api-service && make clean-all
cd ../worker-service && make clean-all
cd .. && docker-compose down -v
```

## 🔧 Troubleshooting

```bash
# Problem: Port 8000 in use
lsof -ti:8000 | xargs kill -9

# Problem: Cannot connect to Kafka
docker-compose restart kafka
sleep 30

# Problem: Cannot connect to Qdrant
docker-compose restart qdrant

# Problem: Worker not processing
docker-compose logs -f worker-service
# Check for errors

# Problem: No search results
# 1. Check if data was pushed
# 2. Wait 5-10 seconds for worker
# 3. Check worker logs
# 4. Check Qdrant collections
curl http://localhost:6333/collections

# Problem: Dependencies error
cd [service-directory]
make clean-all
make setup
```

## 📊 Monitoring

```bash
# API endpoints
open http://localhost:8000/docs          # Swagger UI
open http://localhost:8000/redoc         # ReDoc
curl http://localhost:8000/health        # Health check

# Qdrant dashboard
open http://localhost:6333/dashboard

# Check collections
curl http://localhost:6333/collections

# Check collection details
curl http://localhost:6333/collections/product_accounting

# Service status
docker-compose ps
cd api-service && make info
cd worker-service && make info
```

## 🎯 Common Tasks

### Add new dependency
```bash
cd [service-directory]
source .venv/bin/activate
pip install new-package
pip freeze > requirements.txt
deactivate
```

### Update embedding model
```bash
cd worker-service
nano .env
# Change EMBEDDING_MODEL=...
make clean
make setup
```

### Change API port
```bash
cd api-service
nano .env
# Change API_PORT=8001
make run
```

### Scale workers (Docker)
```bash
docker-compose up -d --scale worker-service=3
```

### Backup Qdrant data
```bash
docker exec qdrant tar czf /tmp/qdrant-backup.tar.gz /qdrant/storage
docker cp qdrant:/tmp/qdrant-backup.tar.gz ./qdrant-backup.tar.gz
```

## 📚 Documentation

```bash
# Main docs
cat README.md
cat QUICKSTART.md
cat ARCHITECTURE.md
cat EXAMPLES.md
cat SETUP_VENV.md

# Service-specific
cat api-service/README.md
cat api-service/README_VENV.md
cat worker-service/README.md
cat worker-service/README_VENV.md
```

## 🎓 Learning Resources

```bash
# 1. Read main README
less README.md

# 2. Quick start
less QUICKSTART.md

# 3. Try examples
python3 test_example.py

# 4. Read API docs
open http://localhost:8000/docs

# 5. Understand architecture
less ARCHITECTURE.md

# 6. See examples
less EXAMPLES.md
```

## ⚡ One-liners

```bash
# Full setup from scratch
docker-compose up -d kafka qdrant && cd api-service && make setup && cd ../worker-service && make setup && cd ..

# Start everything (after setup)
docker-compose up -d kafka qdrant && (cd api-service && make run &) && (cd worker-service && make run &)

# Stop everything
docker-compose down && pkill -f "python -m app"

# Clean everything
cd api-service && make clean-all && cd ../worker-service && make clean-all && cd .. && docker-compose down -v

# Quick test
docker-compose up -d kafka qdrant && sleep 30 && python3 test_example.py

# Check all services
docker-compose ps && curl -s http://localhost:8000/health && curl -s http://localhost:6333/health
```

## 💡 Pro Tips

1. **Use tmux/screen**: Để chạy nhiều terminals
2. **Use make dev**: Cho development với auto-reload/debug
3. **Check logs first**: Khi có lỗi, xem logs trước
4. **Wait after start**: Infrastructure cần 30s để ready
5. **Use venv for dev**: Nhanh hơn Docker cho development
6. **Use Docker for prod**: Stable hơn cho production

## 🎉 Success Indicators

```bash
# All good if you see:
✅ docker-compose ps          # All services "Up"
✅ curl localhost:8000/health # {"message": "Service is healthy"}
✅ curl localhost:6333/health # {"status": "ok"}
✅ python3 test_example.py    # All tests pass
```

