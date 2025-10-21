.PHONY: help venv install clean run dev test lint format

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PYTHON_VENV := $(BIN)/python
PIP := $(BIN)/pip

help:
	@echo "API Service - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Create venv + install (one command)"
	@echo ""
	@echo "Run:"
	@echo "  make run         - Run API service"
	@echo "  make dev         - Run with auto-reload"
	@echo ""
	@echo "Development:"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Check code style"
	@echo "  make format      - Format code"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove virtual environment"
	@echo "  make clean-all   - Remove venv + cache files"
	@echo ""

# Create virtual environment
venv:
	@echo "🔧 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "✅ Virtual environment created at $(VENV)"
	@echo ""
	@echo "To activate manually:"
	@echo "  source $(VENV)/bin/activate"

# Install dependencies
install: venv
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Setup everything (venv + install)
setup: install
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Start infrastructure: cd .. && docker-compose up -d kafka qdrant"
	@echo "  3. Run API: make run"

# Run API service
run:
	@echo "🚀 Starting API service..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "⚠️  .env file not found. Copying from .env.example..."; \
		cp .env.example .env; \
	fi
	$(PYTHON_VENV) -m app.main

# Run with auto-reload (development mode)
dev:
	@echo "🔧 Starting API service in development mode..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ ! -f ".env" ]; then \
		echo "⚠️  .env file not found. Copying from .env.example..."; \
		cp .env.example .env; \
	fi
	$(BIN)/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test (placeholder - add your tests)
test:
	@echo "🧪 Running tests..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "⚠️  No tests configured yet"

# Lint code
lint:
	@echo "🔍 Checking code style..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if ! $(PIP) show flake8 > /dev/null 2>&1; then \
		echo "Installing flake8..."; \
		$(PIP) install flake8; \
	fi
	$(BIN)/flake8 app --max-line-length=120 --exclude=__pycache__

# Format code
format:
	@echo "✨ Formatting code..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if ! $(PIP) show black > /dev/null 2>&1; then \
		echo "Installing black..."; \
		$(PIP) install black; \
	fi
	$(BIN)/black app --line-length=120

# Clean virtual environment
clean:
	@echo "🧹 Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed!"

# Clean everything
clean-all: clean
	@echo "🧹 Removing cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Show current environment info
info:
	@echo "📊 Environment Information:"
	@echo ""
	@if [ -d "$(VENV)" ]; then \
		echo "✅ Virtual environment: EXISTS"; \
		echo "   Path: $(VENV)"; \
		if [ -f "$(PYTHON_VENV)" ]; then \
			echo "   Python: $$($(PYTHON_VENV) --version)"; \
		fi; \
	else \
		echo "❌ Virtual environment: NOT FOUND"; \
	fi
	@echo ""
	@if [ -f ".env" ]; then \
		echo "✅ .env file: EXISTS"; \
	else \
		echo "⚠️  .env file: NOT FOUND"; \
	fi
	@echo ""
	@if [ -f "requirements.txt" ]; then \
		echo "📦 Dependencies:"; \
		cat requirements.txt | grep -v "^#" | grep -v "^$$"; \
	fi

# Check if infrastructure is running
check-infra:
	@echo "🔍 Checking infrastructure..."
	@echo ""
	@echo "Kafka (localhost:9092):"
	@nc -z localhost 9092 && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "Qdrant (localhost:6333):"
	@curl -s http://localhost:6333/health > /dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "To start infrastructure:"
	@echo "  cd .. && docker-compose up -d kafka qdrant"

