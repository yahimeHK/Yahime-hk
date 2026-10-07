@echo off
REM ---------------------------------------------------------------------------
REM  LOL 攻略站 - 啟動本機伺服器並開啟首頁。
REM  直接雙擊這個檔案即可。需要 PATH 上有 Python 3。
REM  用 serve.py 而不是 python -m http.server，是因為影片拖曳時間軸需要
REM  byte range（206）支援。
REM ---------------------------------------------------------------------------

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo   在 PATH 上找不到 Python。
  echo.
  echo   請到 https://www.python.org/downloads/ 安裝 Python 3，
  echo   安裝時記得勾選 "Add python.exe to PATH"，然後再執行一次。
  echo.
  pause
  exit /b 1
)

echo.
echo   正在啟動 LOL 攻略站...
echo   瀏覽器視窗馬上就會開啟。
echo.
echo   觀看期間請保留這個視窗。按 Ctrl+C 可停止。
echo.

REM 先開瀏覽器 - 伺服器慢一點起來時瀏覽器自己會重試
start "" http://127.0.0.1:8099/

python serve.py 8099
if errorlevel 1 (
  echo.
  echo   伺服器已停止。如果 8099 埠被佔用，可以試：python serve.py 8123
  echo.
  pause
)

endlocal
