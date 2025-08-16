import sqlite3, argparse, os, json, time, subprocess, hashlib

DB_PATH = os.path.join(os.getcwd(), ".qwen_ctx.db")

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS notes(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  title TEXT NOT NULL,
  text TEXT NOT NULL,
  tags TEXT
);
CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  session TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  summary TEXT NOT NULL,
  diff_sha TEXT NOT NULL,
  diff TEXT NOT NULL
);
"""

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def ensure_schema(conn):
    conn.executescript(SCHEMA); conn.commit()

def cmd_save(args):
    conn = db(); ensure_schema(conn)
    conn.execute(
        "INSERT INTO notes(ts,title,text,tags) VALUES(?,?,?,?)",
        (int(time.time()), args.title, args.text, args.tags)
    )
    conn.commit(); print("OK: note saved")

def cmd_msg(args):
    conn = db(); ensure_schema(conn)
    conn.execute(
        "INSERT INTO messages(ts,session,role,content) VALUES(?,?,?,?)",
        (int(time.time()), args.session, args.role, args.content)
    )
    conn.commit(); print("OK: message saved")

def git_diff(cached=False):
    try:
        cmd = ["git","diff","--cached"] if cached else ["git","diff"]
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL) \
                         .decode("utf-8","ignore")
    except Exception:
        return ""

def cmd_snapshot(args):
    conn = db(); ensure_schema(conn)
    diff = git_diff(getattr(args, "cached", False))
    sha = hashlib.sha1(diff.encode("utf-8")).hexdigest()
    summary = args.summary or "git diff"
    conn.execute(
        "INSERT INTO snapshots(ts,summary,diff_sha,diff) VALUES(?,?,?,?)",
        (int(time.time()), summary, sha, diff)
    )
    conn.commit(); print("OK: snapshot saved", sha)

def cmd_last(args):
    conn = db(); ensure_schema(conn)
    cur = conn.execute(
        "SELECT ts,title,substr(text,1,160) FROM notes ORDER BY id DESC LIMIT ?",
        (args.limit,)
    )
    for ts, title, text in cur.fetchall():
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        print(f"{t} | {title} | {text.replace('\n',' ')}")

def cmd_dump(args):
    conn = db(); ensure_schema(conn)
    out = {"notes":[], "messages":[], "snapshots":[]}
    for tbl in out.keys():
        cur = conn.execute(f"SELECT * FROM {tbl}")
        cols=[c[0] for c in cur.description]
        out[tbl]=[dict(zip(cols,row)) for row in cur.fetchall()]
    with open(args.path,"w",encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=2))
    print("OK: dumped to", args.path)

def cmd_snaps(args):
    conn = db(); ensure_schema(conn)
    cur = conn.execute(
        "SELECT ts, summary, substr(diff,1,200) FROM snapshots ORDER BY id DESC LIMIT ?",
        (args.limit,)
    )
    rows = cur.fetchall()
    if not rows:
        print("No snapshots"); return
    for ts, summary, diff_head in rows:
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
        one = (diff_head or "").replace("\n"," ")
        print(f"{t} | {summary} | {one}")

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p=sub.add_parser("save")
    p.add_argument("--title", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--tags", default="")
    p.set_defaults(func=cmd_save)

    p=sub.add_parser("msg")
    p.add_argument("--session", required=True)
    p.add_argument("--role", required=True, choices=["user","assistant"])
    p.add_argument("--content", required=True)
    p.set_defaults(func=cmd_msg)

    p=sub.add_parser("snapshot")
    p.add_argument("--summary", default="")
    p.add_argument("--cached", action="store_true")
    p.set_defaults(func=cmd_snapshot)

    p=sub.add_parser("last")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_last)

    p=sub.add_parser("dump")
    p.add_argument("--path", default=".qwen_ctx_dump.json")
    p.set_defaults(func=cmd_dump)

    p=sub.add_parser("snaps")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_snaps)

    args = ap.parse_args()
    args.func(args)
