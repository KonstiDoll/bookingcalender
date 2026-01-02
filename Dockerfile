FROM python:3.11-slim

WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung kopieren
COPY app.py .
COPY static/ static/

# Datenverzeichnis erstellen
RUN mkdir -p /data

# Port freigeben
EXPOSE 5000

# Umgebungsvariablen
ENV FLASK_APP=app.py
ENV DATABASE=/data/bookings.db

# Anwendung starten
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
