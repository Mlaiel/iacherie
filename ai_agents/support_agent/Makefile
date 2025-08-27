# Makefile for Support Agent - Ultra-Advanced AI Customer Support System
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

.PHONY: help install test lint format build run deploy clean docs

# Default target
help:
	@echo "Support Agent - Ultra-Advanced AI Customer Support System"
	@echo "Author: Fahed Mlaiel <mlaiel@live.de>"
	@echo ""
	@echo "Available targets:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests with coverage"
	@echo "  lint       Run linting (flake8, mypy)"
	@echo "  format     Format code (black, isort)"
	@echo "  build      Build Docker image"
	@echo "  run        Run development server"
	@echo "  deploy     Deploy with docker-compose"
	@echo "  clean      Clean cache and build files"
	@echo "  docs       Generate documentation"
	@echo "  security   Run security checks"
	@echo "  benchmark  Run performance benchmarks"

# Development Setup
install:
	@echo "Installing Support Agent dependencies..."
	pip install -r requirements.txt
	pip install -e .

# Testing
test:
	@echo "Running tests with coverage..."
	python -m pytest test_support_agent.py -v \
		--cov=. \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-fail-under=85

test-integration:
	@echo "Running integration tests..."
	python -m pytest test_support_agent.py::TestPerformance -v -s

# Code Quality
lint:
	@echo "Running linting checks..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy . --ignore-missing-imports

format:
	@echo "Formatting code..."
	black . --line-length=100
	isort . --profile=black

# Security
security:
	@echo "Running security checks..."
	safety check
	bandit -r . -f json -o security-report.json
	@echo "Security report saved to security-report.json"

# Docker Operations
build:
	@echo "Building Docker image..."
	docker build -t ia-support-agent:latest .

build-dev:
	@echo "Building development Docker image..."
	docker build -t ia-support-agent:dev --target development .

# Development Server
run:
	@echo "Starting development server..."
	python -m uvicorn support_agent.server:app --host 0.0.0.0 --port 8080 --reload

run-docker:
	@echo "Starting server in Docker..."
	docker run -p 8080:8080 -e SUPPORT_ENVIRONMENT=development ia-support-agent:dev

# Deployment
deploy:
	@echo "Deploying with docker-compose..."
	docker-compose up -d --build

deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

stop:
	@echo "Stopping services..."
	docker-compose down

# Database Operations
db-init:
	@echo "Initializing database..."
	python -c "from support_agent.database import init_db; init_db()"

db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose down postgres
	docker volume rm support-agent_postgres_data
	docker-compose up -d postgres
	sleep 10
	make db-init

# Monitoring
logs:
	@echo "Showing application logs..."
	docker-compose logs -f support-agent

metrics:
	@echo "Opening metrics dashboard..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin123)"

# Performance
benchmark:
	@echo "Running performance benchmarks..."
	python -c "
import asyncio
import time
from test_support_agent import TestPerformance
test = TestPerformance()
asyncio.run(test.test_concurrent_request_handling())
"

stress-test:
	@echo "Running stress tests..."
	docker run --rm -i loadimpact/k6 run - <scripts/stress-test.js

# Documentation
docs:
	@echo "Generating documentation..."
	sphinx-build -b html docs docs/_build/html
	@echo "Documentation available at docs/_build/html/index.html"

docs-serve:
	@echo "Serving documentation locally..."
	python -m http.server 8000 --directory docs/_build/html

# Maintenance
clean:
	@echo "Cleaning cache and build files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf dist/ build/

clean-docker:
	@echo "Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f

# Environment Setup
setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	source venv/bin/activate && make install
	pre-commit install

setup-prod:
	@echo "Setting up production environment..."
	@echo "Generating production secrets..."
	@python -c "
import secrets
print(f'SUPPORT_ENCRYPTION_KEY={secrets.token_urlsafe(32)}')
print(f'SUPPORT_JWT_SECRET={secrets.token_urlsafe(32)}')
print(f'SUPPORT_DB_PASSWORD={secrets.token_urlsafe(16)}')
print(f'GRAFANA_PASSWORD={secrets.token_urlsafe(12)}')
" > .env.prod
	@echo "Production secrets saved to .env.prod"

# Health Checks
health:
	@echo "Checking service health..."
	curl -f http://localhost:8080/health || echo "Service not healthy"
	curl -f http://localhost:8080/metrics || echo "Metrics not available"

# Backup & Restore
backup:
	@echo "Creating backup..."
	docker exec ia-support-postgres pg_dump -U support_user ia_influencer_support > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"

restore:
	@read -p "Enter backup file path: " backup_file; \
	docker exec -i ia-support-postgres psql -U support_user ia_influencer_support < $$backup_file
	@echo "Database restored successfully"

# Development Utilities
shell:
	@echo "Opening Python shell with context..."
	python -c "
from support_agent import SupportAgent, SupportAgentManager
from support_agent.config import get_config
print('Support Agent development shell')
print('Available: SupportAgent, SupportAgentManager, get_config')
import IPython; IPython.start_ipython(argv=[])
"

db-shell:
	@echo "Opening database shell..."
	docker exec -it ia-support-postgres psql -U support_user ia_influencer_support

redis-shell:
	@echo "Opening Redis shell..."
	docker exec -it ia-support-redis redis-cli

# Version and Release
version:
	@python -c "from support_agent import __version__; print(__version__)"

tag-release:
	@read -p "Enter version (current: $$(make version)): " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version
	@echo "Release tagged and pushed"

# All-in-one targets
dev: clean install format lint test
	@echo "Development setup complete!"

ci: install lint test security
	@echo "CI checks passed!"

production: clean build deploy-prod
	@echo "Production deployment complete!"
