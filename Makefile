.PHONY: dev dev-stop migrate test lint format help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start docker services (postgres + redis)
	docker compose up -d

dev-stop: ## Stop docker services
	docker compose down

migrate: ## Run database migrations
	cd backend && alembic upgrade head

test: ## Run tests
	cd backend && python -m pytest -v

lint: ## Run linter
	cd backend && ruff check app/ tests/

format: ## Run formatter
	cd backend && ruff format app/ tests/
