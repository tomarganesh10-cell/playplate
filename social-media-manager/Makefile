.PHONY: help up down build logs shell-backend shell-db seed crawl generate

DOCKER=docker-compose
BACKEND=backend

help:
	@echo "Playplate AI Social Media Manager"
	@echo "=================================="
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make build       - Rebuild all images"
	@echo "make logs        - View all logs"
	@echo "make logs-api    - View backend logs"
	@echo "make seed        - Seed knowledge base"
	@echo "make crawl       - Crawl client website"
	@echo "make generate    - Trigger content generation"
	@echo "make shell-db    - Open database shell"
	@echo "make backup      - Backup database"
	@echo "make status      - Check service status"

up:
	$(DOCKER) up -d
	@echo "✅ Services started"
	@echo "   Dashboard: http://localhost"
	@echo "   API Docs:  http://localhost/api/docs"
	@echo "   n8n:       http://localhost/n8n"

down:
	$(DOCKER) down

build:
	$(DOCKER) build --no-cache

logs:
	$(DOCKER) logs -f

logs-api:
	$(DOCKER) logs -f backend

status:
	$(DOCKER) ps

seed:
	curl -X POST http://localhost/api/knowledge-base/seed \
		-H "Authorization: Bearer $${API_TOKEN}" \
		-s | python3 -m json.tool

crawl:
	curl -X POST http://localhost/api/knowledge-base/crawl \
		-H "Authorization: Bearer $${API_TOKEN}" \
		-s | python3 -m json.tool

generate:
	curl -X POST http://localhost/api/content/generate/daily \
		-H "Authorization: Bearer $${API_TOKEN}" \
		-s | python3 -m json.tool

shell-backend:
	$(DOCKER) exec backend bash

shell-db:
	$(DOCKER) exec postgres psql -U smm -d smm_db

backup:
	$(DOCKER) exec postgres pg_dump -U smm smm_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up"

restart-backend:
	$(DOCKER) restart backend

update:
	git pull origin main
	$(DOCKER) up -d --build backend frontend
	@echo "✅ Updated and restarted"
