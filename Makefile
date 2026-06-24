## Trading Playplate — common dev/ops commands
.DEFAULT_GOAL := help
COMPOSE := docker compose
COMPOSE_MON := docker compose -f docker-compose.yml -f docker-compose.monitoring.yml

.PHONY: help build up down logs ps migrate revision seed test lint fmt \
        backend-shell db-shell monitoring backup restart

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

build: ## Build all images
	$(COMPOSE) build

up: ## Start the core stack (detached)
	$(COMPOSE) up -d

down: ## Stop the stack
	$(COMPOSE) down

restart: ## Restart all services
	$(COMPOSE) restart

logs: ## Tail logs (use S=backend to filter)
	$(COMPOSE) logs -f $(S)

ps: ## Show running services
	$(COMPOSE) ps

migrate: ## Apply DB migrations
	$(COMPOSE) exec backend alembic upgrade head

revision: ## Create a new migration (M="message")
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(M)"

seed: ## Create the first admin user (interactive env: ADMIN_EMAIL/ADMIN_PASSWORD)
	$(COMPOSE) exec backend python -m app.scripts.create_admin

demo: ## One-command local simulation demo with seeded data (http://localhost:8080)
	bash deploy/demo.sh

test: ## Run backend tests
	$(COMPOSE) exec backend pytest -q

lint: ## Lint backend
	$(COMPOSE) exec backend ruff check app tests

fmt: ## Format backend
	$(COMPOSE) exec backend ruff format app tests

backend-shell: ## Shell into backend container
	$(COMPOSE) exec backend bash

db-shell: ## psql into the database
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-playplate} -d $${POSTGRES_DB:-playplate}

monitoring: ## Start stack with Prometheus + Grafana
	$(COMPOSE_MON) up -d

backup: ## Dump the database to ./backups
	bash deploy/backup_db.sh
