.PHONY: install install-frontend dev dev-backend dev-frontend run docker-up docker-down clean

# Install all dependencies
install: install-backend install-frontend

install-backend:
	cd backend && python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

# Run both frontend and backend (development)
dev:
	@echo "Starting backend on http://localhost:8001"
	@echo "Starting frontend on http://localhost:5173"
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn main:app --reload --port 8001

dev-frontend:
	cd frontend && npm run dev

# Run locally with PostgreSQL
run:
	cd backend && . .venv/bin/activate && \
		DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ferienhaus \
		uvicorn main:app --reload --port 8001

# Build frontend for production
build:
	cd frontend && npm run build

# Start with Docker (PostgreSQL + App)
docker-up:
	docker compose up --build -d

# Stop Docker containers
docker-down:
	docker compose down

# Clean up
clean:
	rm -rf backend/.venv backend/__pycache__ backend/*.db
	rm -rf frontend/node_modules frontend/dist
	docker compose down -v 2>/dev/null || true
