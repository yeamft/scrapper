"""
PostgreSQL database connection and helpers.

Env vars: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
Optional: POSTGRES_POOL_SIZE (e.g. 5) to enable connection pooling for the API.
Load from .env if python-dotenv is installed.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import psycopg2
from contextlib import contextmanager
from typing import Generator

def _config():
    return {
        "host": os.environ.get("POSTGRES_HOST", "138.226.240.119"),
        "port": int(os.environ.get("POSTGRES_PORT", "5434")),
        "dbname": os.environ.get("POSTGRES_DB", "test_db"),
        "user": os.environ.get("POSTGRES_USER", "test_user"),
        "password": os.environ.get("POSTGRES_PASSWORD", "test_12311"),
    }

# Optional connection pool (used when POSTGRES_POOL_SIZE is set)
_pool = None

def _get_pool():
    global _pool
    if _pool is not None:
        return _pool
    try:
        size = int(os.environ.get("POSTGRES_POOL_SIZE", "0"))
    except ValueError:
        size = 0
    if size > 0:
        from psycopg2 import pool
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=size,
            **_config()
        )
        return _pool
    return None

class _PooledConnection:
    """Wraps a pooled connection so .close() returns it to the pool."""
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
    def cursor(self, *a, **k):
        return self._conn.cursor(*a, **k)
    def commit(self):
        return self._conn.commit()
    def close(self):
        if self._pool is not None:
            self._pool.putconn(self._conn)
        else:
            self._conn.close()
        self._conn = None
    def __enter__(self):
        return self
    def __exit__(self, *a):
        self.close()

def get_connection():
    """Return a connection. Call .close() when done (or use connection() context manager)."""
    p = _get_pool()
    if p is not None:
        return _PooledConnection(p.getconn(), p)
    return psycopg2.connect(**_config())

def return_connection(conn):
    """Close or return connection to pool. Prefer: with connection() as conn: ..."""
    conn.close()

@contextmanager
def connection() -> Generator:
    """Context manager: yields a connection and closes it (or returns to pool)."""
    conn = get_connection()
    try:
        yield conn
    finally:
        return_connection(conn)

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
