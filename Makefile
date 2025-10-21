.PHONY: help up down restart logs logs-api logs-worker test clean status health

help:
	@echo "MISA MIMOSA ONLINE AI - Semantic Search System"
	@echo ""
	@echo "Available commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View all logs"
	@echo "  make logs-api    - View API service logs"
	@echo "  make logs-worker - View worker service logs"
	@echo "  make status      - Check services status"
	@echo "  make health      - Check API health"
	@echo "  make test        - Run test script"
	@echo "  make clean       - Stop and remove all containers and volumes"
	@echo ""

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "   API: http://localhost:8000"
	@echo "   Qdrant: http://localhost:6333"
	@echo "   Swagger: http://localhost:8000/docs"

down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart
	@echo "✅ Services restarted!"

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api-service

logs-worker:
	docker-compose logs -f worker-service

status:
	@echo "📊 Services status:"
	docker-compose ps

health:
	@echo "🏥 Checking API health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API not responding"

test:
	@echo "🧪 Running test script..."
	python3 test_example.py

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete!"

# Development commands
dev-api:
	@echo "🔧 Starting API in development mode..."
	cd api-service && python -m app.main

dev-worker:
	@echo "🔧 Starting worker in development mode..."
	cd worker-service && python -m app.kafka_consumer

install-api:
	@echo "📦 Installing API dependencies..."
	cd api-service && pip install -r requirements.txt

install-worker:
	@echo "📦 Installing worker dependencies..."
	cd worker-service && pip install -r requirements.txt

install-all: install-api install-worker
	@echo "✅ All dependencies installed!"

