.PHONY: up down logs build clean dev

# Docker commands
up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build

clean:
	docker-compose down -v
	docker system prune -f

# Development commands
dev:
	docker-compose up

# Individual service commands
api-logs:
	docker-compose logs -f api

web-logs:
	docker-compose logs -f web

worker-logs:
	docker-compose logs -f worker

# Database commands
db-shell:
	docker-compose exec api python -c "from app.db.base import SessionLocal; db = SessionLocal(); import code; code.interact(local=locals())"
