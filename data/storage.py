import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stocks.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            ticker TEXT PRIMARY KEY,
            price REAL,
            pe_ratio REAL,
            eps_growth REAL,
            debt_to_equity REAL,
            market_cap REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment (
            ticker TEXT PRIMARY KEY,
            score REAL,
            reasoning TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Tables created successfully")

def save_stock(ticker, price, pe_ratio, eps_growth, debt_to_equity, market_cap):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO stocks 
            (ticker, price, pe_ratio, eps_growth, debt_to_equity, market_cap)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker, price, pe_ratio, eps_growth, debt_to_equity, market_cap))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB save error for {ticker}: {e}")
        return False

def save_sentiment(ticker, score, reasoning):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sentiment (ticker, score, reasoning)
            VALUES (?, ?, ?)
        ''', (ticker, score, reasoning))
        conn.commit()
        conn.close()
        print(f"DB save successful for {ticker}")
        return True
    except Exception as e:
        print(f"DB save error for {ticker}: {e}")
        return False

def get_all_stocks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stocks')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_sentiment():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sentiment')
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_table()