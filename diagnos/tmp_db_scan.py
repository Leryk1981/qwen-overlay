import os
import glob
import sqlite3
import json
import time

def score_db(p):
    s = 0
    t = {"has_tables": 0, "has_views": 0, "has_migrations": 0, "integrity": 0}
    try:
        con = sqlite3.connect(p)
        cur = con.cursor()
        cur.execute("SELECT name,type FROM sqlite_master")
        rows = cur.fetchall()
        names = {r[0] for r in rows}
        types = {r[1] for r in rows}
        if any(r[1] == "table" for r in rows):
            s += 2
            t["has_tables"] = 1
        if any(r[1] == "view" for r in rows):
            s += 2
            t["has_views"] = 1
        if "schema_migrations" in names:
            s += 3
            t["has_migrations"] = 1
        try:
            cur.execute("PRAGMA integrity_check;")
            ok = cur.fetchone()[0] == "ok"
            if ok:
                s += 3
                t["integrity"] = 1
        except:
            pass
        con.close()
    except Exception as e:
        # print(f"Error scoring {p}: {e}") # For debugging
        pass
    # Bonus for recent modification (within last 7 days)
    try:
        s += min(1, int((time.time() - os.path.getmtime(p)) < 7 * 24 * 3600))
    except:
        pass
    return s, t

# Find candidates
cands = set()
# Patterns to search for DB files
patterns = ("state/*.db", "*.db", "**/*.db")
for pat in patterns:
    # Limit recursion depth for "**" patterns
    if "**" in pat:
        for p in glob.glob(pat, recursive=False): # recursive=False for safety, we'll handle depth manually if needed
            if p.endswith(".db") and os.path.isfile(p) and "venv" not in p and ".git" not in p:
                # Check depth
                rel_path = os.path.relpath(p, ".")
                depth = rel_path.count(os.sep)
                if depth <= 3: # Obey depth limit of 3 as per instructions
                     cands.add(os.path.abspath(p))
    else:
        for p in glob.glob(pat):
            if p.endswith(".db") and os.path.isfile(p) and "venv" not in p and ".git" not in p:
                cands.add(os.path.abspath(p))

# Evaluate candidates
out = []
for p in sorted(cands):
    sc, tags = score_db(p)
    out.append({"path": p, "score": sc, **tags})

# Sort by score (desc) then path (asc)
out = sorted(out, key=lambda x: (-x["score"], x["path"]))[:10] # Top 10

print(json.dumps(out, ensure_ascii=False, indent=2))