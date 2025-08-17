import sqlite3
import os

db_path = r"D:\\Projects_Clean\\MOVA_3.0\\state\\sessions.db"
print(f"Validating DB at: {db_path}")

if not os.path.exists(db_path):
    print("DB file does not exist.")
    exit(1)

required_items = {
    "table": ["schema_migrations"],
    "view": ["v_events_flat", "v_llm_events", "v_tool_events"]
}

score = 0
found_items = {"has_tables": 0, "has_views": 0, "has_migrations": 0, "integrity": 0}

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # Check for required items
    cur.execute("SELECT name, type FROM sqlite_master")
    rows = cur.fetchall()
    names = {r[0] for r in rows}
    types = {r[1] for r in rows}
    
    # Check for tables
    if any(r[1] == "table" for r in rows):
        found_items["has_tables"] = 1
        score += 2
    # Check for views
    if any(r[1] == "view" for r in rows):
        found_items["has_views"] = 1
        score += 2
    # Check for specific required tables
    for item in required_items.get("table", []):
        if item in names:
            found_items["has_migrations"] = 1
            score += 3
            break
            
    # Check integrity
    try:
        cur.execute("PRAGMA integrity_check;")
        result = cur.fetchone()
        if result and result[0] == "ok":
            found_items["integrity"] = 1
            score += 3
            print("Integrity check: OK")
        else:
            print(f"Integrity check failed: {result}")
    except Exception as e:
        print(f"Error during integrity check: {e}")
    
    con.close()
    print(f"Validation score: {score}")
    print(f"Found items: {found_items}")
    
    # List some items for debugging
    print("\nSQLite Master (first 10):")
    for r in rows[:10]:
        print(f"  {r[0]} ({r[1]})")

except Exception as e:
    print(f"Error validating DB: {e}")
    exit(1)