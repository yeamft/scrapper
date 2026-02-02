"""
PostgreSQL database connection and helpers.
Uses env vars: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
"""
import os
import psycopg2

def _config():
    return {
        "host": os.environ.get("POSTGRES_HOST", "138.226.240.119"),
        "port": int(os.environ.get("POSTGRES_PORT", "5434")),
        "dbname": os.environ.get("POSTGRES_DB", "test_db"),
        "user": os.environ.get("POSTGRES_USER", "test_user"),
        "password": os.environ.get("POSTGRES_PASSWORD", "test_12311"),
    }

def get_connection():
    """Return a new psycopg2 connection. Caller must close it."""
    return psycopg2.connect(**_config())

def init_database():
    """Create accommodations table if it does not exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accommodations (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    processed_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error TEXT
                )
            """)
        conn.commit()
        print("Database initialized successfully (PostgreSQL)")
    finally:
        conn.close()
