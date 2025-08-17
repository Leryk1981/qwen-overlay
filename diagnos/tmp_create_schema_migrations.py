import sqlite3
import os

db_path = r"D:\Projects_Clean\MOVA_3.0\state\sessions.db"
print(f"Creating schema_migrations table in DB: {db_path}")

if not os.path.exists(db_path):
    print("DB file does not exist.")
    exit(1)

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # Create schema_migrations table
    # Based on common practices, it usually has columns like version, name, applied_at
    # We'll use a simple structure for now.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );
    """)
    print("Table schema_migrations created.")
    
    # Insert records for migrations we know were applied (from tmp_db_fix.py run)
    # We'll use the filename as 'name' and a dummy version/timestamp for now.
    # A more robust system would parse the filename for a version number.
    applied_migrations = [
        ("006_sql_ops_min_schema", "006_sql_ops_min_schema.sql"),
        ("007_sql_ops_views", "007_sql_ops_views.sql"), 
        ("008_sql_ops_fts", "008_sql_ops_fts.sql"),
        ("006_policy_store", "006_policy_store.sql"),
        # Note: 009_seed_smoke.sql failed, so we don't add it here.
    ]
    
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    
    for version, name in applied_migrations:
        try:
            cur.execute(
                "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                (version, name, timestamp)
            )
            print(f"  Recorded migration: {name}")
        except sqlite3.IntegrityError:
            # If it already exists, that's fine.
            print(f"  Migration already recorded: {name}")

    con.commit()
    con.close()
    print("schema_migrations table populated.")

except Exception as e:
    print(f"Error creating/populating schema_migrations table: {e}")
    exit(1)