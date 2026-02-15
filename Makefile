.PHONY: up down run-service

up:
	docker compose -f infrastructure/local/docker-compose.yml up -d

down:
	docker compose -f infrastructure/local/docker-compose.yml down

run-service:
	uvicorn app.main:app --app-dir services/integration-service --reload --port 8080
