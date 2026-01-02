.PHONY: install dev run docker-up docker-down clean

# Install dependencies
install:
	cd backend && python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# Run locally with SQLite (development)
dev:
	cd backend && . .venv/bin/activate && uvicorn main:app --reload --port 8001

# Run locally with PostgreSQL
run:
	cd backend && . .venv/bin/activate && \
		DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ferienhaus \
		uvicorn main:app --reload --port 8001

# Start with Docker (PostgreSQL + App)
docker-up:
	docker compose up --build -d

# Stop Docker containers
docker-down:
	docker compose down

# Clean up
clean:
	rm -rf backend/.venv backend/__pycache__ backend/*.db
	docker compose down -v 2>/dev/null || true
