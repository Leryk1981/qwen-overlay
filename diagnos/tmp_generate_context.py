import sqlite3
import os
import json

# Get DB path
db_path = os.environ.get("DB", r"D:\\Projects_Clean\\MOVA_3.0\\state\\sessions.db")
print(f"Generating context from DB: {db_path}")

if not os.path.exists(db_path):
    print("DB file does not exist.")
    exit(1)

try:
    con = sqlite3.connect(db_path)
    # Enable row factory to get dict-like rows
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Query to get recent events from v_events_flat
    # We'll get the last 150 events ordered by timestamp descending
    # Then reverse the list to have them in ascending order in the context
    cur.execute("""
        SELECT * FROM v_events_flat 
        ORDER BY ts DESC 
        LIMIT 150
    """)
    rows = cur.fetchall()
    
    # Convert rows to list of dicts
    events_list = [dict(row) for row in reversed(rows)] # Reverse to chronological order
    
    con.close()
    
    # Format the context as specified
    context_output = "BEGIN_CTX\n" + json.dumps(events_list, ensure_ascii=False, indent=2) + "\nEND_CTX"
    
    # Write to context_events.json
    context_file = "context_events.json"
    with open(context_file, "w", encoding="utf-8") as f:
        f.write(context_output)
    
    print(f"Context generated and written to {context_file}")
    print(f"Number of events included: {len(events_list)}")

except Exception as e:
    print(f"Error generating context: {e}")
    # It's okay if context generation fails, the DB itself is fixed.
    exit(0) # Exit with 0 to not break the overall process