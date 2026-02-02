"""Script to show database structure and contents (PostgreSQL)."""
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("=" * 80)
print("DATABASE INFORMATION (PostgreSQL)")
print("=" * 80)

# Show table structure
print("\n[1] Table Structure:")
print("-" * 80)
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'accommodations'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    print(f"  {row[0]:20} {row[1]:20} nullable={row[2]:5} default={row[3]}")

# Show current data
print("\n[2] Current Data:")
print("-" * 80)
cursor.execute("SELECT * FROM accommodations ORDER BY id")
rows = cursor.fetchall()

if rows:
    print(f"{'ID':<5} | {'URL':<50} | {'Phone':<15} | {'Processed':<20} | {'Created':<20} | {'Error'}")
    print("-" * 150)
    for row in rows:
        url_display = (row[1][:47] + "...") if len(row[1]) > 50 else row[1]
        phone_display = row[2] if row[2] else "NULL"
        processed_display = str(row[3]) if row[3] else "NULL"
        created_display = str(row[4]) if row[4] else "NULL"
        error_display = (row[5][:30] + "...") if row[5] and len(row[5]) > 30 else (row[5] if row[5] else "NULL")
        print(f"{row[0]:<5} | {url_display:<50} | {phone_display:<15} | {processed_display:<20} | {created_display:<20} | {error_display}")
else:
    print("No data in database")

# Statistics
print("\n[3] Statistics:")
print("-" * 80)
cursor.execute("SELECT COUNT(*) FROM accommodations")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM accommodations WHERE phone IS NOT NULL")
with_phone = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM accommodations WHERE phone IS NULL AND error IS NULL")
pending = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM accommodations WHERE error IS NOT NULL")
errors = cursor.fetchone()[0]
print(f"Total accommodations: {total}")
print(f"With phone numbers: {with_phone}")
print(f"Pending processing: {pending}")
print(f"With errors: {errors}")

print("\n" + "=" * 80)
print("Database type: PostgreSQL")
print("=" * 80)

conn.close()
