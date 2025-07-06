@echo off
echo Installing Telegram Bot as Windows Service...
echo This requires NSSM (Non-Sucking Service Manager)

REM Download NSSM if not exists
if not exist "nssm.exe" (
    echo Downloading NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    copy "nssm-2.24\win64\nssm.exe" "nssm.exe"
    del "nssm.zip"
    rmdir /s /q "nssm-2.24"
)

REM Install service
nssm install TelegramQuizBot python.exe "%cd%\run_bots_forever.py"
nssm set TelegramQuizBot AppDirectory "%cd%"
nssm set TelegramQuizBot DisplayName "Telegram Quiz Bot Service"
nssm set TelegramQuizBot Description "Runs Teacher and Student Telegram Bots"
nssm set TelegramQuizBot Start SERVICE_AUTO_START

echo Service installed! Starting service...
nssm start TelegramQuizBot

echo.
echo ✅ Telegram Quiz Bot is now running as a Windows Service!
echo 🔄 It will start automatically when Windows boots
echo 🛑 To stop: nssm stop TelegramQuizBot
echo 🗑️ To remove: nssm remove TelegramQuizBot
pause
