"""
Einfacher Buchungskalender für Ferienwohnung
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

DATABASE = os.environ.get('DATABASE', 'bookings.db')

# Datenbank beim Start initialisieren
def init_db():
    """Datenbank initialisieren"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Bei Import initialisieren
init_db()

# Die 5 Parteien mit ihren Farben
PARTIES = {
    1: {"name": "Familie Müller", "color": "#4CAF50"},    # Grün
    2: {"name": "Familie Schmidt", "color": "#2196F3"},   # Blau
    3: {"name": "Familie Weber", "color": "#FF9800"},     # Orange
    4: {"name": "Familie Fischer", "color": "#9C27B0"},   # Lila
    5: {"name": "Familie Wagner", "color": "#F44336"},    # Rot
}

def get_db():
    """Datenbankverbindung herstellen"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Hauptseite"""
    return send_from_directory('static', 'index.html')

@app.route('/api/parties', methods=['GET'])
def get_parties():
    """Alle Parteien abrufen"""
    return jsonify(PARTIES)

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Alle Buchungen abrufen"""
    conn = get_db()
    cursor = conn.execute('SELECT * FROM bookings ORDER BY start_date')
    bookings = []
    for row in cursor:
        bookings.append({
            'id': row['id'],
            'party_id': row['party_id'],
            'start_date': row['start_date'],
            'end_date': row['end_date'],
            'note': row['note'],
            'party_name': PARTIES[row['party_id']]['name'],
            'party_color': PARTIES[row['party_id']]['color']
        })
    conn.close()
    return jsonify(bookings)

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Neue Buchung erstellen"""
    data = request.json

    # Validierung
    if not data.get('party_id') or not data.get('start_date') or not data.get('end_date'):
        return jsonify({'error': 'Bitte alle Felder ausfüllen'}), 400

    if data['party_id'] not in PARTIES:
        return jsonify({'error': 'Ungültige Partei'}), 400

    # Prüfen ob Zeitraum bereits gebucht
    conn = get_db()
    cursor = conn.execute('''
        SELECT * FROM bookings
        WHERE (start_date <= ? AND end_date >= ?)
           OR (start_date <= ? AND end_date >= ?)
           OR (start_date >= ? AND end_date <= ?)
    ''', (data['end_date'], data['start_date'],
          data['start_date'], data['start_date'],
          data['start_date'], data['end_date']))

    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Dieser Zeitraum ist bereits gebucht!'}), 409

    # Buchung speichern
    conn.execute('''
        INSERT INTO bookings (party_id, start_date, end_date, note)
        VALUES (?, ?, ?, ?)
    ''', (data['party_id'], data['start_date'], data['end_date'], data.get('note', '')))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Buchung erfolgreich gespeichert!'})

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Buchung löschen"""
    conn = get_db()
    conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Buchung gelöscht'})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
