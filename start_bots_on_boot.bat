@echo off
REM This script starts the bots and can be added to Windows startup

echo Starting Telegram Quiz Bots...
cd /d "%~dp0"
python run_bots_forever.py

REM If the script exits, wait and restart
timeout /t 10
goto :start
