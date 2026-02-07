import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()

# Get all tables and their row counts
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]

print(f"Total tables: {len(tables)}\n")
print(f"{'Table':<40} {'Rows':>15}")
print("-" * 60)

for table in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"{table:<40} {count:>15,}")
    except:
        print(f"{table:<40} {'ERROR':>15}")

cur.close()
conn.close()
