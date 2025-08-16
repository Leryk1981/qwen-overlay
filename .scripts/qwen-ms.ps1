param(
  [string]$Model = "qwen3-coder-flash"
)

# Завантаження .env (якщо є)
$dotenvPath = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $dotenvPath) {
  Get-Content $dotenvPath | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $idx = $_.IndexOf('=')
    if ($idx -gt 0) {
      $name = $_.Substring(0,$idx).Trim()
      $value = $_.Substring($idx+1).Trim()
      [Environment]::SetEnvironmentVariable($name, $value)
      $env:$name = $value
    }
  }
} else {
  Write-Host "WARN: .env not found at $dotenvPath"
}

# Значення за замовчуванням
if (-not $env:OPENAI_BASE_URL) {
  $env:OPENAI_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
}

if (-not $env:OPENAI_API_KEY) {
  Write-Error "OPENAI_API_KEY not set. Fill it in .env"
  exit 1
}

$env:OPENAI_MODEL = $Model

# Запуск Qwen CLI
qwen
