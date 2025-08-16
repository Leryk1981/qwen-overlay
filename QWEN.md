# QWEN — швидкий старт

## Запуски в VS Code
- **Qwen (OAuth)** → Tasks: Run Task → *Qwen (OAuth)*
- **Model Studio**:
  - *Qwen: Flash (Model Studio)*
  - *Qwen: Plus (Model Studio)*
  - *Qwen: 7B (OPS/SQLite)*

## Промпти (Tasks → Copy: … → встав у чат)
- CONDUCTOR — головна сесія (диригент)
- DEV_HEAVY_plus — для qwen3-coder-plus
- DEV_LIGHT_flash — для qwen3-coder-flash
- OPS_CTX_7b — для qwen2.5-coder-7b-instruct (лише ctx.py)

## OPS (SQLite)
Основні команди:
- Зберегти нотатку:
  python .tools/ctx.py save --title "…" --text "…" --tags dev
- Перегляд:
  python .tools/ctx.py last --limit 20
  python .tools/ctx.py snaps --limit 20
- Снапшот git:
  python .tools/ctx.py snapshot --summary "…"

База: `.qwen_ctx.db` (локально, у корені).  
Проєктна карта: `.qwen_project_files.txt`.

## Моделі
- PLUS  → qwen3-coder-plus (важкі задачі/рефакторинг)
- FLASH → qwen3-coder-flash (дрібні правки/тести, дешеві довгі промпти)
- OPS   → qwen2.5-coder-7b-instruct (контекст/логи через ctx.py)

## Нотатки
- Відповіді моделей мають бути **мінімальні**: code/diff або CLI.
- Великі зміни — малими пачками; після кожної — `snapshot`.
