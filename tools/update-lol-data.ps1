#requires -version 5.1
<#
  LOL 攻略站 — 自動更新資料（Riot Data Dragon）
  ------------------------------------------------------------------
  這個腳本會重新產生「英雄資料庫」與「裝備攻略」兩頁的內容與圖片：
    tools/build_champions.py  -> champions.html / champions-db.* / assets/lol/champions.json
    tools/build_items.py      -> items.html / items.css

  由「LOL 攻略站 更新資料」排程工作每週執行一次，也可以雙擊桌面上的
  「立即更新資料.bat」手動執行。跑完之後，站上的「自動推送」工作會在
  幾分鐘內把變更提交並推上 GitHub，GitHub Pages 會自動重新部署。
#>
[CmdletBinding()]
param(
  [string]$RepoPath = ''
)

$ErrorActionPreference = 'Continue'

# 參數區拿不到 $PSScriptRoot，所以在這裡才解析（腳本放在 tools\ 內，上一層就是網站根目錄）
if (-not $RepoPath) { $RepoPath = Split-Path -Parent $PSScriptRoot }
if (-not $RepoPath) { $RepoPath = (Get-Location).Path }

$logDir = Join-Path $env:LOCALAPPDATA 'LOLGuideAutoPush'
$logPath = Join-Path $logDir 'update-data.log'
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }

function Write-Log([string]$Message) {
  $line = '[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
  Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
  Write-Host $line
}

# 找 Python：優先用 DSH 內附的執行環境，其次才是系統的 python
$candidates = @(
  (Join-Path $env:USERPROFILE '.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'),
  'python',
  'py'
)
$python = $null
foreach ($c in $candidates) {
  if ($c -eq 'python' -or $c -eq 'py') {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
  } elseif (Test-Path -LiteralPath $c) {
    $python = $c; break
  }
}
if (-not $python) {
  Write-Log '找不到 Python，無法更新資料。請安裝 Python 3 或確認 DSH 執行環境存在。'
  exit 1
}

# 讓 Python 的輸出用 UTF-8，log 才不會變亂碼
$env:PYTHONIOENCODING = 'utf-8'
try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }

$tools = Join-Path $RepoPath 'tools'
Write-Log ('開始更新 LOL 資料（Python: {0}）' -f $python)

foreach ($script in 'build_champions.py', 'build_items.py', 'build_extra.py', 'build_i18n.py') {
  $path = Join-Path $tools $script
  if (-not (Test-Path -LiteralPath $path)) { Write-Log ('跳過：找不到 {0}' -f $path); continue }
  $out = & $python $path 2>&1
  $code = $LASTEXITCODE
  foreach ($line in $out) { Write-Log ('  ' + ($line -replace '\s+$', '')) }
  Write-Log ('{0} 結束（exit {1}）' -f $script, $code)
}

Write-Log '更新完成，變更會在幾分鐘內由「自動推送」工作提交並發布。'
