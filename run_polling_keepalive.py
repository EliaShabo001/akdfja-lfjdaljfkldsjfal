#!/usr/bin/env python3
"""
Run the bot in polling + keep-alive mode for testing
"""

import os
import subprocess
import sys

def run_polling_keepalive():
    """Run the bot in polling + keep-alive mode"""
    print("🚀 Starting Telegram Quiz Bot in POLLING + KEEP-ALIVE mode...")
    print("📡 This mode combines polling with HTTP server for Cloud Run")
    print("🔄 Bot will poll Telegram while HTTP server handles keep-alive requests")
    print("🌐 HTTP server will run on http://localhost:8080")
    print("💬 Test the bot by sending /start to your bot on Telegram")
    print("🔄 Press Ctrl+C to stop\n")
    
    # Set environment variable and run
    env = os.environ.copy()
    env['DEPLOYMENT_MODE'] = 'polling_keepalive'
    
    try:
        subprocess.run([sys.executable, 'TelegramBot.py'], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")

if __name__ == "__main__":
    run_polling_keepalive()
