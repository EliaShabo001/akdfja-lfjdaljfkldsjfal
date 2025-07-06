#!/usr/bin/env python3
"""
Google Cloud Run 24/7 Bot Runner
This script keeps the Telegram Quiz Bot running continuously on Google Cloud Run
by combining polling with HTTP keep-alive endpoints and self-monitoring.
"""

import os
import sys
import threading
import time
import subprocess
import signal
import requests
from datetime import datetime, timedelta

class CloudRunBotManager:
    def __init__(self):
        self.teacher_process = None
        self.student_process = None
        self.webserver_thread = None
        self.monitor_thread = None
        self.self_ping_thread = None
        self.running = True
        self.restart_count = 0
        self.start_time = datetime.now()
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def start_webserver(self):
        """Start the Flask webserver for keep-alive"""
        try:
            from webserver import keep_alive, start_self_ping
            
            self.log("🌐 Starting HTTP server for keep-alive...")
            keep_alive()
            
            # Start self-ping to keep service alive
            start_self_ping()
            
            self.log("✅ HTTP server started successfully")
            return True
        except Exception as e:
            self.log(f"❌ Failed to start webserver: {e}")
            return False
    
    def kill_existing_bots(self):
        """Kill any existing bot processes"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                             capture_output=True, check=False)
            else:  # Linux/Unix
                subprocess.run(["pkill", "-f", "TelegramBot.py"], 
                             capture_output=True, check=False)
                subprocess.run(["pkill", "-f", "StudentBot.py"], 
                             capture_output=True, check=False)
            time.sleep(2)
        except Exception as e:
            self.log(f"⚠️ Could not kill existing processes: {e}")
    
    def start_teacher_bot(self):
        """Start the teacher bot process"""
        try:
            self.log("🎓 Starting Teacher Bot...")
            
            env = os.environ.copy()
            env['ENVIRONMENT'] = 'cloud_run'
            
            self.teacher_process = subprocess.Popen(
                [sys.executable, "TelegramBot.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=None if os.name == 'nt' else os.setsid
            )
            
            time.sleep(3)
            
            if self.teacher_process.poll() is None:
                self.log("✅ Teacher Bot started successfully")
                return True
            else:
                self.log("❌ Teacher Bot failed to start")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting Teacher Bot: {e}")
            return False
    
    def start_student_bot(self):
        """Start the student bot process"""
        try:
            self.log("👨‍🎓 Starting Student Bot...")
            
            self.student_process = subprocess.Popen(
                [sys.executable, "StudentBot.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=None if os.name == 'nt' else os.setsid
            )
            
            time.sleep(3)
            
            if self.student_process.poll() is None:
                self.log("✅ Student Bot started successfully")
                return True
            else:
                self.log("❌ Student Bot failed to start")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting Student Bot: {e}")
            return False
    
    def check_bot_health(self):
        """Check if both bots are still running"""
        teacher_alive = (self.teacher_process and 
                        self.teacher_process.poll() is None)
        student_alive = (self.student_process and 
                        self.student_process.poll() is None)
        
        return teacher_alive, student_alive
    
    def restart_bots(self):
        """Restart both bots"""
        self.restart_count += 1
        self.log(f"🔄 Restarting bots (restart #{self.restart_count})...")
        
        # Kill existing processes
        self.kill_existing_bots()
        
        # Start fresh
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if teacher_ok and student_ok:
            self.log("✅ Both bots restarted successfully")
            return True
        else:
            self.log("❌ Failed to restart one or both bots")
            return False
    
    def monitor_bots(self):
        """Monitor bot health and restart if needed"""
        self.log("👀 Starting bot health monitor...")
        
        while self.running:
            try:
                teacher_alive, student_alive = self.check_bot_health()
                
                if not teacher_alive or not student_alive:
                    self.log("💀 One or both bots have died!")
                    self.log(f"Teacher Bot: {'✅ Running' if teacher_alive else '❌ Dead'}")
                    self.log(f"Student Bot: {'✅ Running' if student_alive else '❌ Dead'}")
                    
                    if not self.restart_bots():
                        self.log("❌ Failed to restart bots, will retry in 30 seconds...")
                        time.sleep(30)
                else:
                    # Both bots are running
                    uptime = datetime.now() - self.start_time
                    self.log(f"✅ Both bots healthy (uptime: {uptime})")
                
                # Check every 2 minutes
                time.sleep(120)
                
            except Exception as e:
                self.log(f"❌ Error in monitor loop: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the complete system"""
        self.log("🚀 Starting Google Cloud Run 24/7 Bot Manager")
        self.log("=" * 60)
        
        # Start webserver first
        if not self.start_webserver():
            self.log("❌ Failed to start webserver, continuing anyway...")
        
        # Kill any existing bots
        self.kill_existing_bots()
        
        # Start both bots
        teacher_ok = self.start_teacher_bot()
        student_ok = self.start_student_bot()
        
        if not (teacher_ok and student_ok):
            self.log("❌ Failed to start one or both bots initially")
            return False
        
        self.log("🎉 System started successfully!")
        self.log("🎓 Teacher Bot: @QuizForCollegeBot")
        self.log("👨‍🎓 Student Bot: @TestStudentCollegeBot")
        self.log("🌐 HTTP endpoints available for keep-alive")
        self.log("💬 Test by sending /start to either bot on Telegram")
        self.log("=" * 60)
        
        # Start monitoring in background
        self.monitor_thread = threading.Thread(target=self.monitor_bots, daemon=True)
        self.monitor_thread.start()
        
        return True
    
    def stop(self):
        """Stop all processes"""
        self.log("🛑 Stopping all processes...")
        self.running = False
        
        if self.teacher_process:
            self.teacher_process.terminate()
        if self.student_process:
            self.student_process.terminate()
        
        self.log("✅ All processes stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Received shutdown signal")
    if 'manager' in globals():
        manager.stop()
    sys.exit(0)

def main():
    """Main function"""
    global manager
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = CloudRunBotManager()
    
    try:
        if manager.start():
            # Keep main thread alive
            while True:
                time.sleep(60)
        else:
            print("❌ Failed to start the system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        manager.stop()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        manager.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
