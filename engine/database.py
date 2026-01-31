import sqlite3
from datetime import datetime

class Vault:
    def __init__(self, db_name="veloma.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # Cognitive Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stress_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                risk_level REAL,
                agency_zone TEXT,
                decision_quality REAL
            )
        ''')
        # Paper Wallet Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet 
            (balance REAL, btc_holdings REAL)
        ''')
        conn.commit()
        conn.close()
        self.initialize_wallet() # Ensure wallet exists on startup

    def initialize_wallet(self, starting_balance=10000.0):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM wallet")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO wallet VALUES (?, ?)", (starting_balance, 0.0))
        conn.commit()
        conn.close()

    def get_wallet(self):
        conn = sqlite3.connect(self.db_name)
        res = conn.execute("SELECT balance, btc_holdings FROM wallet").fetchone()
        conn.close()
        return res

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
        cursor.execute('SELECT risk_level, decision_quality FROM stress_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        data = cursor.fetchall()
        conn.close()
        return data[::-1]

    def execute_trade(self, trade_type, amount_usd, price):
        balance, holdings = self.get_wallet()
        conn = sqlite3.connect(self.db_name)
        
        if trade_type == "BUY" and balance >= amount_usd:
            new_balance = balance - amount_usd
            new_holdings = holdings + (amount_usd / price)
            conn.execute("UPDATE wallet SET balance = ?, btc_holdings = ?", (new_balance, new_holdings))
        elif trade_type == "SELL" and holdings > 0:
            # Sell all logic for the MVP
            new_balance = balance + (holdings * price)
            conn.execute("UPDATE wallet SET balance = ?, btc_holdings = 0", (new_balance,))
            
        conn.commit()
        conn.close()