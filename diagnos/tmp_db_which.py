import os

# Define paths
repo = os.getcwd()
dotenv_path = os.path.join(repo, '.env')
default_db_path = os.path.join(repo, 'state', 'sessions.db')

print(f"Repository: {repo}")
print(f"Checking for DB path...")

# 1. Check environment variable DB
env_db = os.environ.get('DB')
if env_db and os.path.exists(env_db):
    print(f"Source: env:DB")
    print(f"Path: {env_db}")
    exit(0)

# 2. Check .env file for MOVA_DB
if os.path.exists(dotenv_path):
    print(f".env file found at: {dotenv_path}")
    try:
        with open(dotenv_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip().startswith('MOVA_DB='):
                    p = line.split('=', 1)[1].strip().strip('"').strip("'")
                    print(f"Found MOVA_DB in .env: {p}")
                    if p and os.path.exists(p):
                        print(f"Source: .env:MOVA_DB")
                        print(f"Path: {p}")
                        exit(0)
                    else:
                        print(f"MOVA_DB path from .env does not exist: {p}")
                        break
    except Exception as e:
        print(f"Error reading .env file: {e}")
else:
    print(".env file not found.")

# 3. Check default path
if os.path.exists(default_db_path):
    print(f"Source: default")
    print(f"Path: {default_db_path}")
    exit(0)
else:
    print(f"Default DB path does not exist: {default_db_path}")

print("Source: None")
print("Path: None")