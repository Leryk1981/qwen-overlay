This directory contains Git hooks for this repo.

Enabled hooks:
- pre-commit: saves git diff to .qwen_ctx.db via .tools/ctx.py before each commit.

To activate:
  git config core.hooksPath .githooks
  git update-index --chmod=+x .githooks/pre-commit

To test:
  git commit --allow-empty -m "hook test"
