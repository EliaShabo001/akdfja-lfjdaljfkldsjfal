import subprocess

# Run all scripts concurrently
subprocess.Popen(['python', 'StudentBot.py'])
subprocess.Popen(['python', 'TelegramBot.py'])
subprocess.Popen(['python', 'run_bots.py'])

# Keep the main process alive (Telegram bots require it)
while True:
    pass
