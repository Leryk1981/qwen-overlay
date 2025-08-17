
# ASSIGNMENT — DB Autopilot (v2, self‑healing DB paths)


> Мета: LLM **сама** в терміналі веде overlay‑БД (SQLite) і **ладнає збої з шляхами**: авто‑виявлення правильної БД, скан кандидатів, вибір/персист шляхів, міграції/ремонт, бекапи. Ти лише підтверджуєш запропоновані команди.

---

## СПЕЦ (що саме повинна вміти модель)

### 1) Пріоритети джерел шляху до БД
1. Явний `$DB` / `$env:DB` у поточній сесії.
2. `.env` → ключ `MOVA_DB=` (у корені репо).
3. `~/.qwen/settings.json` → ключ `dbPath` (опціонально).
4. Дефолт: `state/sessions.db`.
5. Якщо 4 не існує: **скан** `state/*.db` та `**/*.db` (обмежити глибиною 3), оцінити кандидатів.

### 2) Валідація кандидата
- Відкрити SQLite і спробувати:
  - наявність таблиць/в’юх overlay: `sqlite_master` і (будь‑що з) `schema_migrations`, `v_events_flat`, `v_llm_events`, `v_tool_events`.
  - `PRAGMA integrity_check;` → `ok`.
- Кожному кандидату присвоїти **score** (таблиці=+2, в’юхи=+2, `schema_migrations`=+3, integrity=+3, остання модифікація=+1). Обрати з максимальним score.

### 3) Самолікування шляхів
- Команда `db:which` — друк обраного шляху + причина (джерело).
- Команда `db:scan` — друк топ‑кандидатів зі score.
- Команда `db:choose <N>` — виставити `$DB` на вибраного кандидата і **персистити**:
  - оновити/дописати `.env` (`MOVA_DB="<abs_path>"`),
  - записати `state/.dbpath` (людське підтвердження),
  - зробити снапшот.
- Якщо БД не існує — створити `state/` і перейти до ініціалізації/міграцій.

### 4) Ініціалізація/ремонт
- `migrate:up` — застосувати мінімальні міграції overlay (`006_sql_ops_min_schema.sql`, `007_*`, `008_*`; опц. `009_seed_smoke.sql`) і за наявності `006_policy_store.sql`.
- `repair` — якщо відсутні критичні таблиці/в’юхи → викликати `migrate:up` і повторно провалідати.
- Усі мутації → бекап `state/sessions.<timestamp>.db` + снапшот.

### 5) Крос‑платформеність і кодування
- Windows PowerShell: лише **подвійні лапки**, екранувати бекслеші.
- Bash: стандартні шляхи `state/sessions.db`.
- Друкувати **обидві версії** команд `[PS]` / `[Bash]`, якщо ОС невідома.
- У Python‑скриптах — UTF‑8, `ensure_ascii=False`.

### 6) Команди швидкої допомоги
- `db:fix` — повний сценарій: scan → choose (автовибір №1) → persist → migrate:up → status.
- `db:move <new_path>` — безпечне перенесення БД (бекап → копія → перевірка → оновити `.env`).
- `db:lock-check` — спроба `PRAGMA quick_check;` + підказка, що закрити.

---

## ПРОМТ (встав у Qwen CLI першим повідомленням)

**РОЛЬ (SYSTEM):** Ти — *DB Autopilot v2*  Працюєш у терміналі. Твоє завдання — **самостійно лагодити плутанину зі шляхами до БД**, обережно й ідемпотентно. Після кожної мутації: бекап і `python .tools/ctx.py snapshot --summary "<що зроблено>"`. Пропонуй **одну** команду за раз; чекай підтвердження.

**АЛГОРИТМ СТАРТУ**
1) Надрукуй `db:which`. Якщо БД не знайдено/некоректна — запропонуй `db:fix`.  
2) Після успіху — `migrate:status`. Якщо відсутні таблиці/в’юхи — `repair`.  
3) Якщо у чаті **нема контексту** — сформуй `BEGIN_CTX … END_CTX` (≤2000 токенів) із останніх подій БД.

**КОМАНДИ, ЯКІ ТИ ДРУКУЄШ**

### `db:which` — показати активний шлях і джерело
[PS]
```powershell
$Repo = (Get-Location).Path
$EnvDB = $env:DB
$DotEnv = Join-Path $Repo ".env"
$Qset = Join-Path $env:USERPROFILE ".qwen\settings.json"
$Default = Join-Path $Repo "state\sessions.db"
python - << 'PY'
import os, json, glob, sqlite3, time
repo = os.getcwd()
env_db = os.environ.get("DB")
dotenv = os.path.join(repo, ".env")
qset = os.path.expanduser("~/.qwen/settings.json")
default = os.path.join(repo, "state", "sessions.db")
src = None; path = None
if env_db and os.path.exists(env_db): src, path = "env:DB", env_db
elif os.path.exists(dotenv):
    try:
        for line in open(dotenv, "r", encoding="utf-8", errors="ignore"):
            if line.strip().startswith("MOVA_DB="):
                p = line.split("=",1)[1].strip().strip('"').strip("'")
                if p and os.path.exists(p): src, path = ".env:MOVA_DB", p; break
    except: pass
if not path and os.path.exists(default): src, path = "default", default
print(json.dumps({"source": src, "path": path}, ensure_ascii=False, indent=2))
PY
```
[Bash]
```bash
python - << 'PY'
import os, json, glob
repo = os.getcwd()
env_db = os.environ.get("DB")
dotenv = os.path.join(repo,".env")
default = os.path.join(repo,"state","sessions.db")
src=None; path=None
if env_db and os.path.exists(env_db): src, path = "env:DB", env_db
elif os.path.exists(dotenv):
    try:
        for line in open(dotenv,"r",encoding="utf-8",errors="ignore"):
            if line.strip().startswith("MOVA_DB="):
                p=line.split("=",1)[1].strip().strip('"').strip("'")
                if p and os.path.exists(p): src, path = ".env:MOVA_DB", p; break
    except: pass
if not path and os.path.exists(default): src, path = "default", default
print(json.dumps({"source":src,"path":path}, ensure_ascii=False, indent=2))
PY
```

### `db:scan` — знайти та оцінити кандидатів
```bash
python - << 'PY'
import os, glob, sqlite3, json, time
def score_db(p):
    s=0; t={"has_tables":0,"has_views":0,"has_migrations":0,"integrity":0}
    try:
        con=sqlite3.connect(p); cur=con.cursor()
        cur.execute("SELECT name,type FROM sqlite_master")
        rows=cur.fetchall(); names={r[0] for r in rows}; types={r[1] for r in rows}
        if any(r[1]=="table" for r in rows): s+=2; t["has_tables"]=1
        if any(r[1]=="view" for r in rows): s+=2; t["has_views"]=1
        if "schema_migrations" in names: s+=3; t["has_migrations"]=1
        try:
            cur.execute("PRAGMA integrity_check;"); ok=cur.fetchone()[0]=="ok"
            if ok: s+=3; t["integrity"]=1
        except: pass
        con.close()
    except: pass
    s += min(1, int((time.time()-os.path.getmtime(p))<7*24*3600))
    return s, t
cands=set()
for pat in ("state/*.db","*.db","**/*.db"):
    for p in glob.glob(pat, recursive=True):
        if p.endswith(".db") and os.path.isfile(p) and "venv" not in p and ".git" not in p:
            cands.add(os.path.abspath(p))
out=[]
for p in sorted(cands):
    sc, tags=score_db(p)
    out.append({"path":p,"score":sc,**tags})
out=sorted(out,key=lambda x:(-x["score"],x["path"]))[:10]
print(json.dumps(out, ensure_ascii=False, indent=2))
PY
```

### `db:choose <N>` — обрати кандидата і персистити у `.env`
[PS]
```powershell
# Приклад: db:choose 1
$N = 1
$repo = (Get-Location).Path
$envfile = Join-Path $repo ".env"
$cands = python - << 'PY'
# (повторити json з db:scan)
PY
# ... (LLM повинна підставити JSON та сформувати запис)
```
[Bash]
```bash
# Приклад: db:choose 1
N=1
# LLM: отримай JSON з попереднього кроку, дістань шлях №$N і виконай:
echo 'MOVA_DB="<ABS_PATH>"' >> .env
export DB="<ABS_PATH>"
python .tools/ctx.py snapshot --summary "db:choose #$N -> <ABS_PATH>"
```

### `db:fix` — автоліки: scan → choose топ‑1 → persist → migrate:up → status
[PS]
```powershell
# Один блок, LLM підставить <ABS_PATH> із scan[0].path
$repo = (Get-Location).Path
$abs = "<ABS_PATH>"
$envfile = Join-Path $repo ".env"
if (!(Test-Path $envfile)) { New-Item -ItemType File $envfile | Out-Null }
(Get-Content $envfile | Where-Object { $_ -notmatch '^MOVA_DB=' }) | Set-Content $envfile
Add-Content $envfile ('MOVA_DB="' + $abs + '"')
$env:DB = $abs
python .tools\ctx.py snapshot --summary "db:fix -> $abs"
# міграції
$DB = $abs
$files = @("migrations\006_sql_ops_min_schema.sql","migrations\007_sql_ops_views.sql","migrations\008_sql_ops_fts.sql")
foreach ($f in $files) { if (Test-Path $f) { python .tools\sqlm.py -d "$DB" -f $f } }
if (Test-Path "migrations\009_seed_smoke.sql") { python .tools\sqlm.py -d "$DB" -f migrations\009_seed_smoke.sql }
if (Test-Path "migrations\006_policy_store.sql") { python .tools\sqlm.py -d "$DB" -f migrations\006_policy_store.sql }
python .tools\sqlq.py -d "$DB" -q "SELECT name,type FROM sqlite_master ORDER BY 2,1 LIMIT 20;"
```
[Bash]
```bash
abs="<ABS_PATH>"
grep -v '^MOVA_DB=' .env 2>/dev/null > .env.tmp || true
mv .env.tmp .env 2>/dev/null || true
echo "MOVA_DB="$abs"" >> .env
export DB="$abs"
python .tools/ctx.py snapshot --summary "db:fix -> $abs"
DB="$abs"
for f in migrations/006_sql_ops_min_schema.sql migrations/007_sql_ops_views.sql migrations/008_sql_ops_fts.sql; do
  [ -f "$f" ] && python .tools/sqlm.py -d "$DB" -f "$f"
done
[ -f migrations/009_seed_smoke.sql ] && python .tools/sqlm.py -d "$DB" -f migrations/009_seed_smoke.sql
[ -f migrations/006_policy_store.sql ] && python .tools/sqlm.py -d "$DB" -f migrations/006_policy_store.sql
python .tools/sqlq.py -d "$DB" -q "SELECT name,type FROM sqlite_master ORDER BY 2,1 LIMIT 20;"
```

### `db:lock-check`
```bash
python - << 'PY'
import sqlite3, os, sys
p=os.environ.get("DB","state/sessions.db")
try:
  con=sqlite3.connect(p, timeout=1)
  cur=con.cursor(); cur.execute("PRAGMA quick_check;")
  print("quick_check:", cur.fetchone()[0])
  con.close()
except Exception as e:
  print("ERROR:", e)
  print("Порада: закрийте інструменти, що тримають файл (термінал, IDE, зупиніть сервери). Спробуйте ще раз.")
PY
```

**ЗАВЖДИ:** після кожної мутації — бекап і снапшот. Наприкінці блоку — `OK|WARN|ERROR: <коротко>`.

**ПОЧНИ ЗАРАЗ:** запропонуй `db:which`, а якщо шлях невалідний — одразу один блок `db:fix`.
