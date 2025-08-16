# Qwen Overlay (VS Code + Hooks + SQLite Context)

## Як використати цей шаблон
1) На GitHub натисни **Use this template** → створи новий репозиторій.
2) Клонуй новий репо.
3) (Опційно) Встанови Qwen CLI:  
   `npm i -g @qwen-code/qwen-code`
4) Скопіюй `.env.example` → `.env` і, коли буде ключ, заповни:

5) Увімкни git hooks:  
`git config core.hooksPath .githooks`
6) У VS Code: **Tasks → Run Task**:
- **Qwen (OAuth)** — працює без ключа
- **Qwen: Flash/Plus/7B (Model Studio)** — коли додаси ключ у `.env`
- **Copy: CONDUCTOR / DEV_* / OPS_CTX_7b** — копіюють промпти в буфер

## Що входить
- `.vscode/` — Tasks (запуск Qwen, копі-промпти)
- `.githooks/` — `pre-commit` (зберігає diff у `.qwen_ctx.db`), `commit-msg` (Conventional Commits)
- `.tools/ctx.py` — локальна SQLite-база контексту
- `.scripts/qwen-ms.ps1` — запуск Qwen з обраною моделлю (DashScope Intl)
- `prompts/` — CONDUCTOR / FLASH / PLUS / OPS
- `.env.example` — зразок змінних середовища
- `.gitattributes` — стабільні переноси рядків
- `QWEN.md` — коротка пам’ятка

## Корисні команди
- `python .tools/ctx.py save --title "..." --text "..." --tags dev`
- `python .tools/ctx.py snapshot --summary "..."`  
- `python .tools/ctx.py last --limit 20` / `python .tools/ctx.py snaps --limit 20`

> `.env` у `.gitignore` — секрети не потраплять у репозиторій.

## TL;DR після клонування
```powershell
git config core.hooksPath .githooks
Copy-Item .env.example .env -Force
```
