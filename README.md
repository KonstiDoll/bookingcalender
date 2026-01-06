# Ferienhaus Kalender

Buchungskalender für Ferienwohnungen - eine einfache Web-App zur Verwaltung von Ferienhausbuchungen für mehrere Familien.

## Tech Stack

**Backend:**
- FastAPI (Python 3.12)
- SQLAlchemy (async) mit SQLite/PostgreSQL
- JWT-Authentifizierung
- Alembic für Migrationen

**Frontend:**
- Vue 3 (Composition API, SFC)
- TypeScript
- Vite
- Tailwind CSS v4

## Voraussetzungen

- Python 3.12+
- Node.js 18+
- (Optional) Docker & Docker Compose

## Installation

```bash
# Alle Dependencies installieren
make install
```

Oder manuell:

```bash
# Backend
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Konfiguration

Kopiere `.env.example` nach `.env` im Backend-Verzeichnis und passe die Werte an:

```bash
cd backend
cp .env.example .env
```

**Wichtige Umgebungsvariablen:**

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `DATABASE_URL` | Datenbank-URL | `sqlite+aiosqlite:///ferienhaus.db` |
| `SESSION_SECRET_KEY` | JWT Secret Key | (generieren!) |
| `PARTY_1_PASSWORD` | Passwort für Familie 1 | - |
| `PARTY_2_PASSWORD` | Passwort für Familie 2 | - |
| `PARTY_3_PASSWORD` | Passwort für Familie 3 | - |
| `PARTY_4_PASSWORD` | Passwort für Familie 4 | - |
| `ADMIN_PASSWORD` | Admin-Passwort | - |

## Development

```bash
# Backend + Frontend parallel starten
make dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8001

### Einzeln starten

```bash
# Nur Backend
make dev-backend

# Nur Frontend
make dev-frontend
```

## Datenbank

### SQLite (Standard)

Keine weitere Konfiguration nötig. Die Datenbank wird automatisch erstellt.

### PostgreSQL

```bash
# DATABASE_URL in .env setzen
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ferienhaus
```

### Migrationen

```bash
# Migrationen anwenden
make migrate

# Neue Migration erstellen
make migrate-new

# Migration rückgängig machen
make migrate-down
```

## Testing

```bash
# Alle Tests
make test

# Nur Backend
make test-backend

# Nur Frontend
make test-frontend
```

**Test-Coverage:**
- Backend: 34 Tests (Auth, Bookings, API)
- Frontend: 29 Tests (Composables)

## Build

```bash
# Frontend für Production bauen
make build
```

## Docker

```bash
# Mit Docker Compose starten (PostgreSQL + App)
make docker-up

# Stoppen
make docker-down
```

## Authentifizierung

Die App verwendet eine einfache Passwort-Authentifizierung:

- Jede Familie hat ein eigenes Passwort (aus Umgebungsvariablen)
- Admin hat Zugriff auf alle Buchungen
- Normale Benutzer können nur ihre eigenen Buchungen verwalten
- JWT-Token mit konfigurierbarer Ablaufzeit

## API Endpunkte

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Aktueller Benutzer |
| GET | `/api/parties` | Alle Familien |
| GET | `/api/bookings` | Alle Buchungen |
| POST | `/api/bookings` | Neue Buchung |
| DELETE | `/api/bookings/{id}` | Buchung löschen |
| GET | `/health` | Health Check |

## Projektstruktur

```
.
├── backend/
│   ├── main.py          # FastAPI App
│   ├── auth.py          # Authentifizierung
│   ├── database.py      # SQLAlchemy Models
│   ├── alembic/         # Migrationen
│   └── tests/           # pytest Tests
├── frontend/
│   ├── src/
│   │   ├── components/  # Vue Components
│   │   ├── composables/ # Vue Composables
│   │   └── types/       # TypeScript Types
│   └── package.json
├── Makefile
└── docker-compose.yml
```

## Lizenz

Private Nutzung
