#!/usr/bin/env python3
"""
Infinite Loop Script - Auto-Execution Every 15 Minutes

This script runs 'python .\\start_all_python.py' every 15 minutes automatically.
Just run this script once with: python infinite_loop.py
It will then run forever in the background, executing the target script every 15 minutes.
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def log_message(message):
    """Print message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def kill_existing_bots():
    """Kill any existing bot processes to prevent conflicts"""
    try:
        # Kill any existing python processes that might be running bots
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            log_message("🔄 Stopped existing bot processes to prevent conflicts")
        time.sleep(2)  # Wait for processes to be fully killed
    except Exception as e:
        log_message(f"⚠️ Could not kill existing processes: {e}")

def run_target_script():
    """Run the target Python script"""
    try:
        log_message("🚀 Starting execution of run_local.py...")

        # First, kill any existing bot processes to prevent conflicts
        kill_existing_bots()

        log_message("🤖 Starting both Teacher Bot and Student Bot...")

        # Start the bot script and let it run
        process = subprocess.Popen(
            [sys.executable, "run_local.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform.startswith('win') else 0
        )

        # Give bots time to start up
        time.sleep(8)

        # Check if the process is still running
        if process.poll() is None:
            log_message("✅ Both bots started successfully and are running!")
            log_message(f"📊 Process ID: {process.pid}")
            log_message("🎓 Teacher Bot: @QuizForCollegeBot")
            log_message("👨‍🎓 Student Bot: @TestStudentCollegeBot")
            log_message("💬 Test by sending /start to either bot on Telegram")
        else:
            # Process exited, check for errors
            stdout, stderr = process.communicate()
            log_message("❌ Bot process exited unexpectedly")
            if stderr:
                log_message("🚨 Error output:")
                print(stderr.decode())
            if stdout:
                log_message("📄 Output:")
                print(stdout.decode())

    except FileNotFoundError:
        log_message("❌ Error: run_local.py not found in current directory")
    except Exception as e:
        log_message(f"❌ Unexpected error: {e}")

def main():
    """Main infinite loop function"""
    log_message("🔄 Infinite Loop Script Started")
    log_message("📋 Will run 'python .\\run_local.py' every 15 minutes")
    log_message("🛑 Press Ctrl+C to stop the loop")
    log_message("=" * 60)
    
    # Check if target script exists
    if not os.path.exists("run_local.py"):
        log_message("⚠️  Warning: run_local.py not found in current directory")
        log_message("📁 Current directory: " + os.getcwd())
        log_message("📋 Make sure run_local.py exists before continuing")
        
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            log_message("🛑 Script stopped by user")
            return
    
    execution_count = 0
    
    try:
        while True:
            execution_count += 1
            log_message(f"🔢 Execution #{execution_count}")
            
            # Run the target script
            run_target_script()
            
            # Calculate next execution time
            from datetime import timedelta
            next_run = datetime.now() + timedelta(minutes=15)
            next_run = next_run.replace(second=0, microsecond=0)
            
            log_message(f"⏰ Next execution scheduled at: {next_run.strftime('%H:%M:%S')}")
            log_message("💤 Waiting 15 minutes...")
            log_message("-" * 60)
            
            # Wait for 15 minutes (900 seconds)
            time.sleep(900)
            
    except KeyboardInterrupt:
        log_message("\n🛑 Infinite loop stopped by user (Ctrl+C)")
        log_message(f"📊 Total executions completed: {execution_count}")
        log_message("👋 Goodbye!")
    except Exception as e:
        log_message(f"💥 Fatal error in main loop: {e}")
        log_message("🔄 Script will exit")

if __name__ == "__main__":
    main()
