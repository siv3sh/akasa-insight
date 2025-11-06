# Makefile for Akasa Air Data Engineering Project

# Variables
DOCKER_COMPOSE = docker-compose
PYTHON = python3
PIP = pip3

# Default target
.PHONY: help
help:
	@echo "Akasa Air Data Engineering Project - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make seed          - Seed database with sample data"
	@echo "  make flow          - Run daily ingestion flow"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run code linting"
	@echo "  make clean         - Clean up temporary files"
	@echo "  make install       - Install dependencies"
	@echo "  make dashboard     - Start Streamlit dashboard"
	@echo "  make migrate       - Run database migrations"

# Start all services
.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d

# Stop all services
.PHONY: down
down:
	$(DOCKER_COMPOSE) down

# Seed database with sample data
.PHONY: seed
seed:
	$(DOCKER_COMPOSE) run app python src/main.py

# Run daily ingestion flow
.PHONY: flow
flow:
	$(DOCKER_COMPOSE) run app python flows/daily_ingestion.py

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v

# Run linting
.PHONY: lint
lint:
	$(PYTHON) -m ruff check src/ flows/ app/
	$(PYTHON) -m ruff format --check src/ flows/ app/

# Clean temporary files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf logs/
	rm -rf outputs/

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Start Streamlit dashboard
.PHONY: dashboard
dashboard:
	$(PYTHON) -m streamlit run app/dashboard.py

# Run database migrations
.PHONY: migrate
migrate:
	$(PYTHON) src/database/migrations.py

# Run backfill
.PHONY: backfill
backfill:
	@echo "Usage: make backfill START_DATE=YYYY-MM-DD END_DATE=YYYY-MM-DD"
	@if [ -z "$(START_DATE)" ] || [ -z "$(END_DATE)" ]; then \
		echo "Error: START_DATE and END_DATE must be provided"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) run app python flows/daily_ingestion.py --backfill-start $(START_DATE) --backfill-end $(END_DATE)