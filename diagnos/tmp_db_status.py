import sqlite3
import os

# Get DB path from environment or default
db_path = os.environ.get("DB", r"D:\Projects_Clean\MOVA_3.0\state\sessions.db")
print(f"Checking status of DB: {db_path}")

if not os.path.exists(db_path):
    print("DB file does not exist.")
    exit(1)

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # Execute the query from the instruction's `migrate:status`
    cur.execute("SELECT name,type FROM sqlite_master ORDER BY 2,1 LIMIT 20;")
    rows = cur.fetchall()
    
    print("SQLite Master (first 20, ordered by type then name):")
    for r in rows:
        print(f"  {r[0]} ({r[1]})")

    con.close()

except Exception as e:
    print(f"Error checking DB status: {e}")
    exit(1)