#!/usr/bin/env python3
"""
Run both Teacher Bot and Student Bot forever with auto-restart
This script keeps both bots running and restarts them if they crash
"""

import subprocess
import time
import sys
import os

def log_message(message):
    """Print message with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def kill_existing_processes():
    """Kill any existing bot processes"""
    # Skip killing processes to avoid conflicts
    log_message("🔄 Starting fresh bot instances...")

def start_bots():
    """Start both bots and return the process"""
    try:
        log_message("🚀 Starting both Teacher Bot and Student Bot...")
        
        process = subprocess.Popen(
            [sys.executable, "run_local.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give bots time to start
        time.sleep(5)
        
        if process.poll() is None:
            log_message("✅ Both bots started successfully!")
            log_message("🎓 Teacher Bot: @QuizForCollegeBot")
            log_message("👨‍🎓 Student Bot: @TestStudentCollegeBot")
            log_message("💬 Test by sending /start to either bot on Telegram")
            return process
        else:
            log_message("❌ Bots failed to start")
            return None
            
    except Exception as e:
        log_message(f"❌ Error starting bots: {e}")
        return None

def main():
    """Main function to keep bots running forever"""
    log_message("🔄 Starting Bot Auto-Restart System")
    log_message("🤖 This will keep both bots running forever")
    log_message("🛑 Press Ctrl+C to stop")
    log_message("=" * 60)
    
    restart_count = 0
    
    try:
        while True:
            restart_count += 1
            log_message(f"🔢 Bot Start/Restart #{restart_count}")
            
            # Kill any existing processes
            kill_existing_processes()
            
            # Start the bots
            bot_process = start_bots()
            
            if bot_process is None:
                log_message("❌ Failed to start bots, retrying in 30 seconds...")
                time.sleep(30)
                continue
            
            # Monitor the bots
            log_message("👀 Monitoring bots... (checking every 60 seconds)")
            
            while True:
                time.sleep(60)  # Check every minute
                
                if bot_process.poll() is not None:
                    # Process has died
                    log_message("💀 Bots have stopped running!")
                    log_message("🔄 Will restart in 10 seconds...")
                    time.sleep(10)
                    break  # Break inner loop to restart
                else:
                    # Still running
                    log_message("✅ Bots are still running...")
            
    except KeyboardInterrupt:
        log_message("\n🛑 Auto-restart system stopped by user")
        log_message(f"📊 Total restarts: {restart_count}")
        
        # Kill the bot process if it's still running
        if 'bot_process' in locals() and bot_process and bot_process.poll() is None:
            bot_process.terminate()
            log_message("🔄 Stopped running bots")
        
        log_message("👋 Goodbye!")

if __name__ == "__main__":
    main()
