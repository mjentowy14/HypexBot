import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        self.db_path = 'trading_logs.db'
        print(f"Initializing database at {self.db_path}")  # Debug print
        self._create_tables()
    
    def _create_tables(self):
        """
        Create tables if they don't exist
        """
        print("Creating tables...")  # Debug print
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                token TEXT,
                current_price REAL,
                allora_prediction REAL,
                prediction_difference_percent REAL,
                volatility_24h REAL,
                trade_direction TEXT,
                entry_price REAL,
                market_condition TEXT,
                reason TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"Database initialized successfully")  # Debug print

    def log_trade(self, trade_data):
        print(f"Attempting to log trade: {trade_data}")  # Debug print
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO trade_logs (
                    timestamp, token, current_price, allora_prediction, 
                    prediction_difference_percent, volatility_24h,
                    trade_direction, entry_price, market_condition, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                trade_data['token'],
                trade_data['current_price'],
                trade_data['allora_prediction'],
                trade_data['prediction_diff'],
                trade_data['volatility'],
                trade_data['direction'],
                trade_data['entry_price'],
                trade_data['market_condition'],
                trade_data.get('reason', None)
            ))
            
            conn.commit()
            print(f"Successfully logged trade")  # Debug print
            
        except Exception as e:
            print(f"Error logging trade: {str(e)}")
        finally:
            conn.close()
    
    def update_trade_result(self, trade_id, exit_price, profit_loss, result):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trade_logs 
            SET exit_price = ?, profit_loss_percent = ?, trade_result = ?
            WHERE id = ?
        """, (exit_price, profit_loss, result, trade_id))
        
        conn.commit()
        conn.close()