"""Clear all rows from the accommodations database (PostgreSQL)."""
from db import get_connection

conn = get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM accommodations")
        n = cur.rowcount
    conn.commit()
    print(f"Cleared {n} row(s). Database is empty.")
finally:
    conn.close()
