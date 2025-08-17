import os
import shutil
import subprocess
import json

# --- 1. Get the path to use (from scan result) ---
# For simplicity in this script, we'll use the known path.
# In a full implementation, you'd parse the output of tmp_db_scan.py.
chosen_path = r"D:\Projects_Clean\MOVA_3.0\state\sessions.db"
print(f"Chosen DB path: {chosen_path}")

# --- 2. Persist the path to .env ---
repo = os.getcwd()
envfile = os.path.join(repo, ".env")
print(f"Updating .env file: {envfile}")

# Read existing .env content
env_lines = []
if os.path.exists(envfile):
    with open(envfile, "r", encoding="utf-8", errors="ignore") as f:
        env_lines = f.readlines()

# Filter out existing MOVA_DB line
env_lines = [line for line in env_lines if not line.strip().startswith("MOVA_DB=")]

# Add new MOVA_DB line
env_lines.append(f'MOVA_DB="{chosen_path}"\n')

# Write back to .env
with open(envfile, "w", encoding="utf-8") as f:
    f.writelines(env_lines)

print(".env file updated.")

# --- 3. Set environment variable for subsequent commands ---
os.environ["DB"] = chosen_path

# --- 4. Run migrations (migrate:up) ---
print("Running migrations...")

# Define migration files to apply
migration_files = [
    "migrations/006_sql_ops_min_schema.sql",
    "migrations/007_sql_ops_views.sql", 
    "migrations/008_sql_ops_fts.sql",
    "migrations/009_seed_smoke.sql", # Optional seed
    "migrations/006_policy_store.sql" # Policy store
]

# Path to sqlm.py tool
sqlm_tool = ".tools/sqlm.py"

# Apply each migration file if it exists
for mig_file in migration_files:
    if os.path.exists(mig_file):
        print(f"  Applying migration: {mig_file}")
        try:
            # Use subprocess.run to capture output and handle errors
            # The command is: python .tools/sqlm.py -d "<DB_PATH>" -f "<MIG_FILE>"
            result = subprocess.run(
                ["python", sqlm_tool, "-d", chosen_path, "-f", mig_file],
                capture_output=True,
                text=True,
                check=True # Raise CalledProcessError on non-zero exit
            )
            # print(f"    stdout: {result.stdout}") # Uncomment for verbose output
            # if result.stderr: print(f"    stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"    ERROR applying {mig_file}: {e}")
            print(f"    stdout: {e.stdout}")
            print(f"    stderr: {e.stderr}")
            # Depending on policy, you might want to stop here or continue
        except FileNotFoundError:
            print(f"    WARNING: Tool {sqlm_tool} not found. Skipping migration {mig_file}.")
    else:
        print(f"  Migration file not found, skipping: {mig_file}")

print("Migrations completed (or failed/skipped as reported above).")

# --- 5. Take a snapshot ---
snapshot_tool = ".tools/ctx.py"
if os.path.exists(snapshot_tool):
    print("Taking a snapshot...")
    try:
        result = subprocess.run(
            ["python", snapshot_tool, "snapshot", "--summary", f"db:fix -> {chosen_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        # print(f"  Snapshot stdout: {result.stdout}")
        # if result.stderr: print(f"  Snapshot stderr: {result.stderr}")
        print("Snapshot taken.")
    except subprocess.CalledProcessError as e:
        print(f"  ERROR taking snapshot: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"  WARNING: Snapshot tool {snapshot_tool} not found.")
else:
    print(f"Snapshot tool not found: {snapshot_tool}")

print("db:fix process finished.")