import sqlite3
import os
import tempfile
import shutil

# --- Налаштування ---
# Створимо тимчасову БД для тестування, скопіювавши поточну
original_db = r"D:\Projects_Clean\MOVA_3.0\state\sessions.db"
test_db_dir = tempfile.mkdtemp(prefix="mova_test_")
test_db_path = os.path.join(test_db_dir, "test_sessions.db")

print(f"Копіюємо оригінальну БД {original_db} до {test_db_path} для тестування...")
shutil.copyfile(original_db, test_db_path)
print("Копіювання завершено.")

# --- Симуляція проблеми: видаляємо таблицю schema_migrations ---
print("\n--- Симуляція проблеми: видалення таблиці schema_migrations ---")
try:
    con = sqlite3.connect(test_db_path)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS schema_migrations;")
    con.commit()
    con.close()
    print("Таблицю schema_migrations видалено.")
except Exception as e:
    print(f"Помилка при видаленні таблиці: {e}")
    exit(1)

# --- Перевірка, що таблиці дійсно немає ---
print("\n--- Перевірка наявності schema_migrations (має бути False) ---")
try:
    con = sqlite3.connect(test_db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations';")
    res = cur.fetchone()
    con.close()
    print(f"Таблиця schema_migrations існує: {res is not None}")
    if res is not None:
        print("ПОМИЛКА: Таблиця не була видалена.")
        exit(1)
except Exception as e:
    print(f"Помилка при перевірці: {e}")
    exit(1)

# --- Симуляція db:fix ---
print("\n--- Симуляція db:fix ---")
# Встановлюємо змінну оточення для тестової БД
os.environ["DB"] = test_db_path

# Імпортуємо логіку з tmp_db_fix.py (який ми зберегли в diagnos)
# Але для простоти, прямо застосуємо міграції через sqlm.py
import subprocess

repo_root = r"D:\Projects_Clean\MOVA_3.0"
sqlm_tool = os.path.join(repo_root, ".tools", "sqlm.py")

# Визначаємо файли міграцій у правильному порядку
migration_files = [
    os.path.join(repo_root, "migrations", "006_sql_ops_min_schema.sql"),
    os.path.join(repo_root, "migrations", "007_sql_ops_views.sql"), 
    os.path.join(repo_root, "migrations", "008_sql_ops_fts.sql"),
]

print("Застосування міграцій...")
for mig_file in migration_files:
    if os.path.exists(mig_file):
        print(f"  Застосовується: {mig_file}")
        try:
            result = subprocess.run(
                ["python", sqlm_tool, "-d", test_db_path, "-f", mig_file],
                capture_output=True,
                text=True,
                check=True,
                cwd=repo_root # Встановлюємо робочу директорію
            )
        except subprocess.CalledProcessError as e:
            print(f"    ПОМИЛКА застосування {mig_file}: {e}")
            print(f"    stderr: {e.stderr}")
            # Продовжуємо, можливо наступні міграції виправлять ситуацію
        except FileNotFoundError:
            print(f"    ПОМИЛКА: Інструмент {sqlm_tool} не знайдено.")
            exit(1)
    else:
        print(f"  Файл міграції не знайдено, пропускається: {mig_file}")

# --- Перевірка, що таблиця schema_migrations була створена ---
print("\n--- Перевірка результату: наявність schema_migrations (має бути True) ---")
try:
    con = sqlite3.connect(test_db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations';")
    res = cur.fetchone()
    con.close()
    exists = res is not None
    print(f"Таблиця schema_migrations існує після міграцій: {exists}")
    if not exists:
        print("ПОМИЛКА: Таблиця schema_migrations НЕ була створена після міграцій.")
        exit(1)
    else:
        print("УСПІХ: Таблиця schema_migrations була успішно створена.")
except Exception as e:
    print(f"Помилка при фінальній перевірці: {e}")
    exit(1)

# --- Очищення ---
print("\n--- Очищення тимчасових файлів ---")
try:
    shutil.rmtree(test_db_dir)
    print(f"Тимчасова директорія {test_db_dir} видалена.")
except Exception as e:
    print(f"Помилка при видаленні тимчасової директорії: {e}")

print("\n--- ТЕСТ ЗАВЕРШЕНО ---")