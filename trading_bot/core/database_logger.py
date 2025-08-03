import sqlite3
from ..core.models import Trade, Signal

def get_db_connection(db_file="trades.db"):
    """Creates a database connection."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

import os

def initialize_db(db_file="trades.db"):
    """Initializes the database, clearing old data and creating fresh tables."""
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed old database file: {db_file}")

    conn = get_db_connection(db_file)
    cursor = conn.cursor()

    # Create Trades Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        trade_id TEXT PRIMARY KEY,
        instrument TEXT NOT NULL,
        direction TEXT NOT NULL,
        entry_timestamp TEXT NOT NULL,
        entry_price REAL NOT NULL,
        entry_fee REAL,
        stop_loss_price REAL,
        size REAL NOT NULL,
        status TEXT NOT NULL,
        exit_timestamp TEXT,
        exit_price REAL,
        exit_fee REAL,
        pnl REAL
    )
    """)

    # Create Signals Table (optional, but good for analysis)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_id TEXT,
        instrument TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        pattern_name TEXT NOT NULL,
        signal_type TEXT NOT NULL,
        direction TEXT NOT NULL,
        confluence_score REAL,
        FOREIGN KEY (trade_id) REFERENCES trades (trade_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def log_trade_to_db(trade: Trade, signal: Signal):
    """Logs a trade and its originating signal to the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Log the signal first
        cursor.execute("""
        INSERT INTO signals (trade_id, instrument, timestamp, pattern_name, signal_type, direction, confluence_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (trade.trade_id, signal.instrument, str(signal.timestamp), signal.pattern_name, signal.signal_type, signal.direction, signal.confluence_score))

        # Log the trade
        cursor.execute("""
        INSERT INTO trades (trade_id, instrument, direction, entry_timestamp, entry_price, entry_fee, stop_loss_price, size, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trade.trade_id, trade.instrument, trade.direction, str(trade.entry_timestamp), trade.entry_price, trade.entry_fee, trade.stop_loss_price, trade.size, trade.status))

        conn.commit()
        print(f"Logged trade {trade.trade_id} to database.")
    except Exception as e:
        print(f"Database logging error: {e}")
        conn.rollback()
    finally:
        conn.close()

def update_trade_in_db(trade: Trade):
    """Updates an existing trade in the database (e.g., when it's closed)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE trades
        SET status = ?, exit_timestamp = ?, exit_price = ?, exit_fee = ?, pnl = ?
        WHERE trade_id = ?
        """, (trade.status, str(trade.exit_timestamp), trade.exit_price, trade.exit_fee, trade.pnl, trade.trade_id))

        conn.commit()
        print(f"Updated closed trade {trade.trade_id} in database.")
    except Exception as e:
        print(f"Database update error: {e}")
        conn.rollback()
    finally:
        conn.close()
