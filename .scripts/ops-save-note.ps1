param(
  [string]$Title,
  [string]$Text,
  [string]$Tags = "ops,handoff"
)
$ErrorActionPreference = "Stop"

# Визначаємо Python
if (Test-Path ".\.venv\Scripts\python.exe") {
  $py = ".\.venv\Scripts\python.exe"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $py = "python"
} else {
  Write-Error "Python not found (no .venv and no 'python' in PATH)"; exit 1
}

# Підказки користувачу
if (-not $Title) { $Title = Read-Host "Title" }
if (-not $Text)  {
  try { $Text = Get-Clipboard } catch { $Text = "" }
}
if (-not $Text)  { $Text = Read-Host "Text (clipboard empty)" }

& $py .tools\ctx.py save --title $Title --text $Text --tags $Tags
