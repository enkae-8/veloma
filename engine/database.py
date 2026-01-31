import sqlite3
from datetime import datetime

class Vault:
    def __init__(self, db_name="veloma.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stress_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                risk_level REAL,
                agency_zone TEXT,
                decision_quality REAL
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, risk, zone, quality):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stress_logs (timestamp, risk_level, agency_zone, decision_quality)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), risk, zone, quality))
        conn.commit()
        conn.close()

    def get_history(self, limit=100):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # FIXED: We now select BOTH risk and quality
        cursor.execute('SELECT risk_level, decision_quality FROM stress_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        data = cursor.fetchall()
        conn.close()
        return data[::-1] # Flip it so the chart moves left to right