param([int]$Limit = 10)
if (Test-Path ".\.venv\Scripts\python.exe") { $py = ".\.venv\Scripts\python.exe" } else { $py = "python" }
& $py .tools\ctx.py last --limit $Limit
